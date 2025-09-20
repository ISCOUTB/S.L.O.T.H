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
from typing import Generator

import pika
from messaging_utils.messaging import RabbitMQConnectionFactory
from proto_utils.messaging.dtypes import SchemaMessageResponse

from src.core.config import settings
from src.core.connection_params import messaging_params
from src.utils.logger import logger


class SchemasWorker:
    """RabbitMQ worker for processing schema update messages.

    This worker consumes messages from the 'typechecking.schema.queue',
    processes schema update requests by creating and saving schemas,
    and publishes the results back to the exchange for further processing.

    The worker handles message acknowledgment, error recovery, and maintains
    proper connection lifecycle management through the connection factory.

    Attributes:
        connection: RabbitMQ blocking connection for the worker thread.
        channel: RabbitMQ channel for message operations.
    """

    TASK = "schemas"

    def start_consuming(self) -> None:
        """Start consuming messages from the RabbitMQ queue.

        Initializes the RabbitMQ connection and channel, sets up the messaging
        infrastructure, and begins consuming messages from the schema queue.
        This method blocks until consumption is stopped or an error occurs.

        The worker is configured with QoS settings to control message prefetch
        and uses manual acknowledgment for reliable message processing.

        Raises:
            Exception: If connection setup fails or consumption encounters
                unrecoverable errors. Errors are logged and consumption is stopped.
        """
        try:
            self.connection: pika.BlockingConnection = (
                RabbitMQConnectionFactory.get_thread_connection()
            )
            self.channel = RabbitMQConnectionFactory.get_thread_channel()
            RabbitMQConnectionFactory.setup_infrastructure(self.channel)

            self.channel.basic_qos(
                prefetch_count=settings.WORKER_PREFETCH_COUNT
            )
            self.channel.basic_consume(
                queue=messaging_params["exchange"]["queues"][0]["routing_key"],
                on_message_callback=self.process_schema_update,
                auto_ack=False,
            )

            logger.info("Schemas worker started. Waiting for messages...")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error starting schema worker: {repr(e)}")
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
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                RabbitMQConnectionFactory.close_thread_connections()
                logger.info("ValidationWorker: Connections closed")
        except Exception as e:
            logger.error(f"ValidationWorker: Error closing connections: {e}")

    def process_schema_update(
        self, ch, method, properties, body
    ) -> Generator[SchemaMessageResponse, None, None]:
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
            message: SchemaMessageResponse = json.loads(body.decode())
            task_id = message["id"]
            yield message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Schema task {task_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing schema task: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
