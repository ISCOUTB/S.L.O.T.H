"""Schema Worker Module.

This module provides a RabbitMQ worker that processes schema update messages
from the typechecking queue system. The SchemaWorker class handles incoming
schema update requests, processes them by creating and saving schemas, and
publishes the results back to the messaging system.

The worker implements proper message acknowledgment, error handling, and
connection management using the RabbitMQ connection factory for thread safety.

Example:
    Running the schema worker:

    >>> from src.workers.schemas import SchemaWorker
    >>> worker = SchemaWorker()
    >>> worker.start_consuming()  # Blocks and processes messages
"""

import json
import time

import pika
from jsonschema import SchemaError
from messaging_utils.core.config import settings as mq_settings
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.schemas import SchemaMessage
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    ChannelClosedByBroker,
)
from proto_utils.database import dtypes

from src.core.config import settings
from src.core.database_client import DatabaseClient, get_database_client
from src.handlers.schemas import create_schema, remove_schema, save_schema
from src.schemas.workers import SchemaUpdated
from src.utils import create_component_logger, get_datetime_now
from src.workers.utils import update_task_status

# Create logger with [schemas] prefix
logger = create_component_logger("schemas")


class SchemaWorker:
    """RabbitMQ worker for processing schema update messages.

    This worker consumes messages from the 'typechecking.schema.queue',
    processes schema update requests by creating and saving schemas,
    and publishes the results back to the exchange for further processing.

    The worker handles message acknowledgment, error recovery, and maintains
    proper connection lifecycle management through the connection factory.

    Attributes:
        max_retries: Maximum number of retries for processing a message.
        retry_delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier for retry delays.
        threshold: Time threshold to reset retry attempts.
        db_client: Database client for task status updates.
        connection: RabbitMQ blocking connection for the worker thread.
        channel: RabbitMQ channel for message operations.
    """

    TASK = "schemas"

    def __init__(
        self,
        max_retries: int,
        retry_delay: float,
        backoff: float,
        threshold: float,
    ) -> None:
        """Initialize the SchemaWorker instance.

        Sets up initial state for the worker, including connection and channel
        placeholders. Actual connection setup is performed in start_consuming().
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff = backoff
        self.threshold = threshold

        self.db_client = get_database_client(logger)
        self.connection: pika.BlockingConnection | None = None
        self.channel: BlockingChannel | None = None

    def start_consuming(self) -> None:
        """Start consuming messages from the RabbitMQ queue with intelligent retry.

        Implements time-based retry strategy with exponential backoff. Distinguishes
        between immediate connection failures and stable connections that later fail.
        Resets retry counter if connection was stable for >= threshold seconds,
        preventing exit after temporary hiccups in long-running workers.

        The worker fails fast after exhausting retries, allowing the orchestrator
        to restart the container with fresh state.

        Retry Strategy:
            - Max retries configurable (default: 5)
            - Exponential backoff (2s → 4s → 8s → 16s → 32s)
            - Stability threshold (default: 60s)
            - Counter resets if uptime >= threshold

        Connection Lifecycle:
            1. Attempt connection with exponential backoff
            2. Start consuming (blocks until connection lost)
            3. On disconnect, check elapsed uptime:
               - If >= threshold: reset retry counter (stable connection)
               - If < threshold: increment counter (unstable/flapping)
            4. Retry or fail-fast if max retries exhausted

        Raises:
            SystemExit: After exhausting retries, exits with code 1 for orchestrator
                restart. Implements fail-fast pattern.
            KeyboardInterrupt: Handled gracefully for manual shutdown.
        """
        logger.info("Starting schema worker...")
        attempts = 0
        current_delay = self.retry_delay
        t0 = time.perf_counter()
        while attempts < self.max_retries:
            try:
                self.connection = (
                    RabbitMQConnectionFactory.get_thread_connection()
                )
                self.channel = RabbitMQConnectionFactory.get_thread_channel()
                RabbitMQConnectionFactory.setup_infrastructure(self.channel)

                self.channel.basic_qos(
                    prefetch_count=settings.WORKER_PREFETCH_COUNT
                )
                self.channel.basic_consume(
                    queue=mq_settings.RABBITMQ_QUEUE_SCHEMAS,
                    on_message_callback=self.process_schema_update,
                    auto_ack=False,
                )

                logger.info("Schema worker started. Waiting for messages...")
                connection_time = time.perf_counter() - t0
                logger.debug(
                    f"Schema worker connected to RabbitMQ in "
                    f"{connection_time:.2f}s."
                )

                t0 = time.perf_counter()
                self.channel.start_consuming()

                # if start_consuming() returns, it means the worker was stopped normally
                logger.info("Schema worker stopped consuming messages.")
                break

            except (
                AMQPConnectionError,
                AMQPChannelError,
                ChannelClosedByBroker,
            ) as e:
                elapsed_time = time.perf_counter() - t0
                if elapsed_time >= self.threshold:
                    logger.info(
                        f"Connection was stable for {elapsed_time:.1f}s. "
                        "Resetting retry counter."
                    )
                    attempts = 0
                    current_delay = self.retry_delay

                if attempts < self.max_retries:
                    logger.warning(
                        f"Schema worker connection error (attempt "
                        f"{attempts + 1}/{self.max_retries}): {repr(e)}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= self.backoff
                    t0 = time.perf_counter()
                else:
                    logger.error(
                        f"Failed to connect to RabbitMQ after "
                        f"{self.max_retries} attempts. "
                        f"Last error: {repr(e)}. "
                        "Exiting. Orchestrator should restart this worker."
                    )
                    self.stop_consuming()
                    raise SystemExit(1) from e

                attempts += 1

            except KeyboardInterrupt:
                logger.info("Schema worker interrupted by user.")
                self.stop_consuming()
                break

            except Exception as e:
                logger.error(f"Error starting schema worker: {repr(e)}")
                self.stop_consuming()
                raise SystemExit(1) from e

        self.stop_consuming()

    def stop_consuming(self) -> None:
        """Stop consuming messages and close the connection.

        Gracefully stops message consumption and closes RabbitMQ connections
        and channels. This method should be called during shutdown or when
        the worker needs to be stopped cleanly.

        Handles cases where connections may already be closed and logs
        the shutdown process for monitoring purposes.
        """
        try:
            logger.info("Stopping schema Worker...")

            if self.db_client:
                self.db_client.close()

            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                RabbitMQConnectionFactory.close_thread_connections()
                logger.info("SchemaWorker: Connections closed")
        except Exception as e:
            logger.error(f"SchemaWorker: Error closing connections: {e}")

    def process_schema_update(self, ch, method, properties, body) -> None:
        """Process incoming schema update messages.

        Handles individual schema update messages by parsing the message body,
        extracting the task information, updating the schema, and publishing
        the result. Implements proper message acknowledgment on success and
        negative acknowledgment on failure.

        Args:
            ch: RabbitMQ channel object for message acknowledgment.
            method: Message delivery method containing delivery tag and routing info.
            properties: Message properties (headers, content-type, etc.).
            body: Raw message body containing the schema update request.

        Message Format:
            Expected message body should be a JSON-encoded ApiResponse containing:
            - task_id: Unique identifier for the schema update task
            - import_name: Name identifier for the schema import
            - schema_params: Parameters needed to create the schema

        Note:
            Failed messages are not requeued to prevent infinite retry loops.
            Error details are logged for debugging and monitoring.
        """
        try:
            message = SchemaMessage(**json.loads(body.decode()))
            task_id = message["id"]
            task = message.get("task", "upload_schema")

            if task == "upload_schema":
                # Update the task status to 'processing'
                logger.info(f"Processing schema update: {task_id}")
                update_task_status(
                    database_client=self.db_client,
                    task_id=task_id,
                    field="status",
                    value="received-schema-update",
                    task=self.TASK,
                    data={
                        "upload_date": message["date"],
                        "update_date": get_datetime_now(),
                    },
                )
                result = self._update_schema(message, db_client=self.db_client)

            if task == "remove_schema":
                logger.info(f"Removing schema: {task_id}")
                update_task_status(
                    database_client=self.db_client,
                    task_id=task_id,
                    field="status",
                    value="received-removing-schema",
                    task=self.TASK,
                    data={
                        "upload_date": message["date"],
                        "update_date": get_datetime_now(),
                    },
                )
                result = self._remove_schema(message, db_client=self.db_client)

            # Add more cases here if needed for other tasks

            # Here could be implemented a callback to notify other services
            # e.g. using webhooks or other messaging patterns.
            # And, maybe, not use another queue of results for that.

            # Meanwhile
            self._publish_result(task_id, result, db_client=self.db_client)

            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(f"Schema update completed for task: {task_id}")
        except Exception as e:
            logger.error(f"Error processing schema update: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _update_schema(
        self, message: SchemaMessage, db_client: DatabaseClient
    ) -> SchemaUpdated:
        """Update the schema based on the incoming message.

        Processes a schema update request by creating a new schema from the
        provided parameters and saving it with the specified import name.
        Returns a structured result containing the operation status and details.

        Args:
            message (SchemaMessage): Dictionary containing schema update parameters including:
                - task_id: Unique task identifier
                - import_name: Schema import identifier
                - schema: Parameters for schema creation
                - raw: Boolean indicating if the schema is raw
            db_client (DatabaseClient): Database client for task status updates.

        Returns:
            SchemaUpdated: Dictionary containing the update result with fields:
                - task_id: Original task identifier
                - status: 'completed' or 'failed' based on operation result
                - import_name: Schema import name
                - schema: Created schema object
                - result: Boolean result from save operation

        Note:
            The function prints the result for debugging purposes and
            determines status based on the save operation success.
        """
        task_id = message["id"]
        import_name = message["import_name"]
        raw = message.get("raw", False)

        # Update the task status
        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="creating-schema",
            task=self.TASK,
            message=f"Creating schema for import: {import_name}",
            data={"update_date": get_datetime_now()},
        )

        # Create the schema from the provided parameters
        try:
            schema = create_schema(raw, message["schema"])
            update_task_status(
                database_client=db_client,
                task_id=task_id,
                field="status",
                value="schema-created",
                task=self.TASK,
                message=f"Schema created for import: {import_name}",
                data={"update_date": get_datetime_now()},
            )
        except SchemaError as e:
            logger.error(f"Schema creation failed: {e}")
            update_task_status(
                database_client=db_client,
                task_id=task_id,
                field="status",
                value="failed-creating-schema",
                task=self.TASK,
                message=repr(e),
                data={"update_date": get_datetime_now()},
            )

            return SchemaUpdated(
                task_id=task_id,
                status="failed-creating-schema",
                import_name=import_name,
                schema=None,
                result=False,
            )

        # Save the schema and return the result
        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="saving-schema",
            task=self.TASK,
            data={"update_date": get_datetime_now()},
        )
        try:
            result = save_schema(
                schema.copy(),
                import_name,
                database_client=db_client,
            )
            status = "completed"
        except Exception as e:
            result = repr(e)
            status = "failed-saving-schema"

        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value=status,
            task=self.TASK,
            message="Validation completed and uploaded to the database.",
            data={
                "results": (
                    repr(result)
                    if result
                    else "Schema is the same, no update needed."
                ),
                "update_date": get_datetime_now(),
            },
        )

        return SchemaUpdated(
            task_id=task_id,
            status=status,
            import_name=import_name,
            schema=schema,
            result=result,
        )

    def _remove_schema(
        self, message: SchemaMessage, db_client: DatabaseClient
    ) -> SchemaUpdated:
        """Remove the schema based on the incoming message.

        Processes a schema removal request by deleting the schema associated
        with the provided import name. Returns a structured result containing
        the operation status and details.

        Args:
            message (SchemaMessage): Dictionary containing schema removal parameters including:
                - task_id: Unique task identifier
                - import_name: Schema import identifier
            db_client (DatabaseClient): Database client instance for database operations.

        Returns:
            SchemaUpdated: Dictionary containing the removal result with fields:
                - task_id: Original task identifier
                - status: 'completed' or 'failed' based on operation result
                - import_name: Schema import name
                - result: Boolean result from removal operation

        Note:
            The function updates the task status and handles errors
            during schema removal.
        """
        task_id = message["id"]
        import_name = message["import_name"]

        # Update the task status
        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="removing-schema",
            task=self.TASK,
            message=f"Removing schema for import: {import_name}",
            data={"update_date": get_datetime_now()},
        )

        # Remove the schema and return the result
        try:
            result = remove_schema(import_name, database_client=db_client)
            status = "completed"
        except Exception as e:
            result = repr(e)
            status = "failed-removing-schema"

        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value=status,
            task=self.TASK,
            message="Schema removal completed.",
            data={
                "results": result if result else "Active Schema not found.",
                "update_date": get_datetime_now(),
            },
        )

        return SchemaUpdated(
            task_id=task_id,
            status=status,
            import_name=import_name,
            schema=None,
            result=result,
        )

    def _publish_result(
        self, task_id: str, result: SchemaUpdated, db_client: DatabaseClient
    ) -> None:
        """Publish the result of the schema update to the RabbitMQ exchange.

        Sends the schema update result to the 'typechecking.exchange' with
        routing key 'schema.result' for downstream consumers to process.

        Args:
            task_id (str): Unique identifier for the completed task, used for logging.
            result (SchemaUpdated): Dictionary containing the schema update result to be published.
                Should be JSON-serializable.
            db_client (DatabaseClient): Database client for task status updates.

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems. Errors are propagated to the caller
                for proper error handling and message acknowledgment.
        """
        if result["status"] != "completed":
            upload_date = db_client.get_task_id(
                dtypes.GetTaskIdRequest(
                    task_id=task_id,
                    task=self.TASK,
                )
            )["value"]["data"].get("upload_date", get_datetime_now())
            update_task_status(
                database_client=db_client,
                task_id=task_id,
                field="status",
                value="failed-publishing-result",
                task=self.TASK,
                message="Failed to publish validation result",
                data={
                    "error": "Failed to publish validation result",
                    "update_date": get_datetime_now(),
                    "upload_date": upload_date,
                },
                reset_data=True,
            )
            logger.error(f"Failed to publish result for task: {task_id}")
            return None

        self.channel.basic_publish(
            exchange=mq_settings.RABBITMQ_EXCHANGE,
            routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_SCHEMAS,
            body=json.dumps(result),
        )
        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="published",
            task=self.TASK,
            message="Validation result published",
            data={"update_date": get_datetime_now()},
        )
        logger.info(f"Validation result published for task: {task_id}")
        return None
