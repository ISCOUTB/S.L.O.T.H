"""Validation Worker Module.

This module provides a RabbitMQ worker that processes file validation messages
from the typechecking queue system. The ValidationWorker class handles incoming
validation requests, validates files against schemas, and publishes the results
back to the messaging system.

The worker processes uploaded files by converting hexadecimal data back to binary,
creating UploadFile objects, and running validation against specified schemas.
Results include detailed validation summaries and status information.

Example:
    Running the validation worker:

    >>> from src.workers.validation import ValidationWorker
    >>> worker = ValidationWorker()
    >>> worker.start_consuming()  # Blocks and processes validation messages
"""

import asyncio
import json
import time
from io import BytesIO

import pika
from fastapi import UploadFile
from messaging_utils.core.config import settings as mq_settings
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.schemas import ValidationMessage
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    ChannelClosedByBroker,
)
from proto_utils.database import dtypes

from src.core.config import settings
from src.core.database_client import DatabaseClient, get_database_client
from src.handlers.validation import (
    get_validation_summary,
    validate_file_against_schema,
)
from src.schemas.workers import DataValidated
from src.utils import create_component_logger, get_datetime_now
from src.workers.utils import update_task_status

# Create logger with [validation] prefix
logger = create_component_logger("validation")


class ValidationWorker:
    """RabbitMQ worker for processing file validation messages.

    This worker consumes messages from the 'typechecking.validation.queue',
    processes file validation requests by validating uploaded files against
    specified schemas, and publishes the validation results back to the exchange.

    The worker handles file data conversion from hexadecimal format back to
    binary, creates proper UploadFile objects, and runs comprehensive validation
    with detailed result summaries.

    Attributes:
        max_retries: Maximum number of retries for processing a message.
        retry_delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier for retry delays.
        threshold: Time threshold to reset retry attempts.
        db_client: Database client for task status updates.
        channel: RabbitMQ channel for message operations.
        publisher: ValidationPublisher instance for publishing results.
        connection: RabbitMQ connection established during consumption.
    """

    TASK: str = "validation"

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
        logger.info("Starting validation worker...")
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
                    queue=mq_settings.RABBITMQ_QUEUE_VALIDATIONS,
                    on_message_callback=self.process_validation_request,
                    auto_ack=False,
                )

                logger.info(
                    "Validation worker started. Waiting for messages..."
                )

                connection_time = time.perf_counter() - t0
                logger.debug(
                    f"Validation worker connected to RabbitMQ in "
                    f"{connection_time:.2f}s."
                )

                t0 = time.perf_counter()
                self.channel.start_consuming()

                # if start_consuming() returns, it means the worker was stopped normally
                logger.info("Validation worker stopped consuming messages.")
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
                        f"Validation worker connection error (attempt "
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
                logger.info("Validation worker interrupted by user.")
                self.stop_consuming()
                break

            except Exception as e:
                logger.error(f"Error starting validation worker: {repr(e)}")
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
            logger.info("Stopping validation worker...")

            if self.db_client:
                self.db_client.close()

            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                RabbitMQConnectionFactory.close_thread_connections()
                logger.info("ValidationWorker: Connections closed")
        except Exception as e:
            logger.error(f"ValidationWorker: Error closing connections: {e}")

    def process_validation_request(self, ch, method, properties, body) -> None:
        """Process a validation request message.

        Handles individual validation request messages by parsing the message body,
        extracting the task information, validating the file data, and publishing
        the result. Implements proper message acknowledgment on success and
        negative acknowledgment on failure.

        Args:
            ch: RabbitMQ channel object for message acknowledgment.
            method: Message delivery method containing delivery tag and routing info.
            properties: Message properties (headers, content-type, etc.).
            body: Raw message body containing the validation request.

        Message Format:
            Expected message body should be a JSON-encoded ApiResponse containing:
            - task_id: Unique identifier for the validation task
            - file_data: Hexadecimal-encoded file content
            - import_name: Schema identifier for validation
            - filename: Optional original filename

        Note:
            Failed messages are not requeued to prevent infinite retry loops.
            Error details are logged for debugging and monitoring.
        """
        try:
            message = ValidationMessage(**json.loads(body.decode()))
            task_id = message["id"]
            task = message.get("task", "sample_validation")

            if task == "sample_validation":
                logger.info(f"Process validation request: {task_id}")
                update_task_status(
                    database_client=self.db_client,
                    task_id=task_id,
                    field="status",
                    value="received-sample-validation",
                    task=self.TASK,
                    data={
                        "upload_date": message["date"],
                        "update_date": get_datetime_now(),
                    },
                )
                result = asyncio.run(
                    self._validate_data(message, db_client=self.db_client)
                )

            # Add more cases here if needed for other tasks

            # Here could be implemented a callback to notify other services
            # e.g. using webhooks or other messaging patterns.
            # And, maybe, not use another queue of results for that.

            # Meanwhile
            self._publish_result(task_id, result, db_client=self.db_client)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Validation completed for task: {task_id}")
        except Exception as e:
            logger.error(f"Error processing validation request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    async def _validate_data(
        self, message: ValidationMessage, db_client: DatabaseClient
    ) -> DataValidated:
        """Validate the incoming message data.

        Processes file validation by converting hexadecimal file data back to
        binary format, creating an UploadFile object, and running validation
        against the specified schema. Returns a structured validation result.

        Args:
            message (ValidationMessage): Dictionary containing validation parameters including:
                - task_id: Unique task identifier
                - file_data: Hexadecimal-encoded file content
                - import_name: Schema identifier for validation
                - filename: Optional original filename (defaults to 'uploaded_file')
            db_client (DatabaseClient): DatabaseClient instance for updating task status.

        Returns:
            DataValidated: Dictionary containing the validation result with fields:
                - task_id: Original task identifier
                - status: Validation status ('valid', 'invalid', etc.)
                - results: Detailed validation summary including error counts,
                  validation details, and any schema violations

        Raises:
            Exception: If file conversion fails, validation encounters errors,
                or schema lookup fails. Errors are propagated to the caller
                for proper message handling.

        Note:
            This method is async due to the validate_file_against_schema
            function requiring async execution for file processing.
        """
        task_id = message["id"]
        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="processing-file",
            task=self.TASK,
            data={"update_date": get_datetime_now()},
        )
        file_bytes = bytes.fromhex(message["file_data"])
        file_obj = BytesIO(file_bytes)
        upload_file = UploadFile(
            filename=message["metadata"]["filename"], file=file_obj
        )

        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value="validating-file",
            task=self.TASK,
            data={"update_date": get_datetime_now()},
        )

        results = await validate_file_against_schema(
            file=upload_file, import_name=message["import_name"]
        )

        logger.debug(f"Results: {json.dumps(results, indent=4)}")

        summary = get_validation_summary(results)

        update_task_status(
            database_client=db_client,
            task_id=task_id,
            field="status",
            value=summary["status"],
            task=self.TASK,
            data={
                "results": json.dumps(summary),
                "update_date": get_datetime_now(),
            },
        )

        return DataValidated(
            task_id=task_id,
            status=summary["status"],
            results=summary,
        )

    def _publish_result(
        self, task_id: str, result: DataValidated, db_client: DatabaseClient
    ) -> str:
        """Publish the validation result back to the exchange.

        Sends the validation result to the 'typechecking.exchange' with
        routing key 'validation.result' for downstream consumers to process.

        Args:
            task_id (str): Unique identifier for the completed validation task,
                used for logging and correlation.
            result (str): Dictionary containing the validation result to be published.
                Should be JSON-serializable and contain validation summary data.
            db_client (DatabaseClient): DatabaseClient instance for updating task status.

        Returns:
            str: Confirmation message indicating the result was published.

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems. Errors are propagated to the caller
                for proper error handling and message acknowledgment.
        """
        if result["status"] == "error":
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
            routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_RESULTS_VALIDATIONS,
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
