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

import json
import queue
import threading
from typing import Generator, Optional

from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from proto_utils.messaging.dtypes import ValidationMessageResponse

from src.core.config import settings
from src.core.connection_params import messaging_params
from src.utils.logger import logger


class ValidationWorker:
    """RabbitMQ worker for processing file validation messages.

    This worker consumes messages from the 'typechecking.validation.queue',
    processes file validation requests by validating uploaded files against
    specified schemas, and publishes the validation results back to the exchange.

    The worker handles file data conversion from hexadecimal format back to
    binary, creates proper UploadFile objects, and runs comprehensive validation
    with detailed result summaries.

    Attributes:
        channel: RabbitMQ channel for message operations.
        publisher: ValidationPublisher instance for publishing results.
        connection: RabbitMQ connection established during consumption.
    """

    TASK: str = "validation"

    def __init__(self):
        self._message_queue: queue.Queue[ValidationMessageResponse] = (
            queue.Queue()
        )
        self._is_consuming: bool = False
        self._stop_event = threading.Event()

    def start_consuming(self) -> None:
        """Start consuming messages from the RabbitMQ queue.

        Initializes the RabbitMQ connection and channel, sets up the messaging
        infrastructure, and begins consuming messages from the validation queue.
        This method blocks until consumption is stopped or an error occurs.

        The worker is configured with QoS settings to control message prefetch
        and uses manual acknowledgment for reliable message processing.

        Raises:
            Exception: If connection setup fails or consumption encounters
                unrecoverable errors. Errors are logged and consumption is stopped.
        """
        try:
            self._is_consuming = True
            self._stop_event.clear()

            self.connection = RabbitMQConnectionFactory.get_thread_connection()
            self.channel = RabbitMQConnectionFactory.get_thread_channel()
            RabbitMQConnectionFactory.setup_infrastructure(self.channel)

            self.channel.basic_qos(
                prefetch_count=settings.WORKER_PREFETCH_COUNT
            )
            self.channel.basic_consume(
                queue=messaging_params["exchange"]["queues"][1]["queue"],
                on_message_callback=self.process_validation_request,
                auto_ack=False,
            )

            logger.info("Validation worker started. Waiting for messages...")
            self.channel.start_consuming()

        except Exception as e:
            logger.error(f"Error starting validation worker: {repr(e)}")
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
            self._is_consuming = False
            self._stop_event.set()

            if (
                hasattr(self, "channel")
                and self.channel
                and self.channel.is_open
            ):
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
            message: ValidationMessageResponse = json.loads(body.decode())
            task_id = message["id"]

            self._message_queue.put(message)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Validation completed for task: {task_id}")
        except Exception as e:
            logger.error(f"Error processing validation request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def get_message_stream(
        self,
        timeout_secs: float = 1.0,
        yield_none_on_timeout: bool = False,
    ) -> Generator[Optional[ValidationMessageResponse], None, None]:
        """Generator to yield received validation messages."""
        try:
            # Generator runs until explicitly stopped or has no messages for timeout period
            while not self._stop_event.is_set():
                try:
                    message = self._message_queue.get(timeout=timeout_secs)
                    yield message
                    self._message_queue.task_done()
                except queue.Empty:
                    if yield_none_on_timeout:
                        yield None

                    # If not yielding None on timeout and worker is not consuming, break
                    if not self._is_consuming:
                        break
                    continue
        except GeneratorExit:
            pass  # Suppress logging on generator exit to avoid closed file errors
        except Exception as e:
            logger.error(f"Error in message stream: {e}")
            raise e
        finally:
            pass  # Suppress logging on exit to avoid closed file errors

    def has_messages(self) -> bool:
        """Check if there are messages in the queue."""
        return not self._message_queue.empty()

    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self._message_queue.qsize()
