"""Message Publishers Module.

This module provides publishers for sending messages to RabbitMQ queues
in the typechecking system. The publishers handle message formatting,
routing, and delivery properties for validation and schema update operations.

Publishers use the factory RabbitMQ connection and handle message
serialization, unique ID generation, and proper message properties
for reliable delivery and processing.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    StreamLostError,
)

from messaging_utils.core.connection_params import messaging_params
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.schemas import (
    AllConnectionParams,
    ConnectionParams,
    ExchangeInfo,
    InsertionMessage,
    InsertionTasks,
    Metadata,
    ValidationMessage,
    ValidationTasks,
)

T = TypeVar("T")


class Publisher:
    """Publisher for messaging service.

    This publisher handles sending validation requests and schema updates
    to the RabbitMQ exchange. It manages message formatting, unique ID
    generation, and proper message properties for reliable delivery.

    The publisher uses the Factory RabbitMQ connection and formats
    messages according to the defined message schemas with appropriate
    routing keys for proper queue distribution.

    Attributes:
        exchange_info: Exchange configuration details.
        _channel: RabbitMQ channel obtained from the factory connection.
    """

    def __init__(
        self,
        params: Optional[ConnectionParams] = None,
        exchange_info: Optional[ExchangeInfo] = None,
        max_tries: int = 5,
        retry_delay: float = 1.0,
        backoff: float = 2.0,
        logger: Optional[logging.Logger] = None,
        *_: Any,
        **__: Any,
    ) -> None:
        """Initialize the Publisher.

        Sets up the publisher with a channel from the factory RabbitMQ
        connection. The channel is used for all message publishing operations.
        """
        self.max_retries = max_tries
        self.retry_delay = retry_delay
        self.backoff = backoff

        if logger is None:
            logging.basicConfig(level=logging.DEBUG)
            logger = logging.getLogger(__name__)
        self.logger = logger

        if params is None:
            tmp = messaging_params.copy()
            tmp.pop("exchange")
            params = tmp

        if exchange_info is None:
            exchange_info = messaging_params["exchange"]

        self.exchange_info = exchange_info

        # If the connection factory is not configured, configure it
        if (
            not hasattr(RabbitMQConnectionFactory, "_params")
            or not RabbitMQConnectionFactory._params
        ):
            RabbitMQConnectionFactory.configure(
                AllConnectionParams(**params, exchange=self.exchange_info)  # type: ignore
            )

        self._channel = RabbitMQConnectionFactory.get_thread_channel()

    def _get_healthy_channel(self, force_new: bool = False) -> BlockingChannel:
        """Get a healthy RabbitMQ channel.

        Ensures that the channel is open and the connection is healthy.
        If not, it retrieves a new channel from the factory connection.

        Args:
            force_new (bool): Force retrieval of a new channel.

        Returns:
            BlockingChannel: Healthy RabbitMQ channel.
        """
        if force_new or not self._channel or not self._channel.is_open:
            self._channel = RabbitMQConnectionFactory.get_thread_channel()
        return self._channel

    def is_healthy_channel(self) -> bool:
        """Check if the current channel is healthy.

        A channel is considered healthy if it is open and the underlying
        connection is open.

        Returns:
            bool: True if the channel is healthy, False otherwise.
        """
        return (
            self._channel
            and self._channel.is_open
            and self._channel.connection
            and self._channel.connection.is_open
        )

    def _execute_with_retry(
        self,
        operation: Callable[[], T],
        operation_name: str,
    ) -> T:
        """Execute a publish operation with automatic retry on failure.

        This method wraps publish operations with retry logic that handles
        connection and channel errors. It uses exponential backoff between
        retries and automatically obtains new channels from the factory
        on connection failures.

        Args:
            operation: Callable that performs the publish operation.
            operation_name: Name of the operation for logging purposes.

        Returns:
            T: Result of the operation (typically task_id string).

        Raises:
            Exception: The last exception encountered if all retries are exhausted.

        Retry Logic:
            - First attempt uses existing channel
            - Subsequent attempts force new channel creation
            - Delay increases exponentially: delay * (backoff ^ attempt)
            - Handles AMQPConnectionError, AMQPChannelError, StreamLostError
        """
        current_delay = self.retry_delay
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Get channel (force new on retries)
                force_new = attempt > 1
                self._get_healthy_channel(force_new=force_new)

                # Execute the operation
                return operation()

            except (
                AMQPConnectionError,
                AMQPChannelError,
                StreamLostError,
            ) as e:
                last_exception = e

                if attempt == self.max_retries:
                    self.logger.warning(
                        f"[Publisher] {operation_name} failed after "
                        f"{self.max_retries} attempts: {e}"
                    )
                    raise

                self.logger.warning(
                    f"[Publisher] {operation_name} failed "
                    f"(attempt {attempt}/{self.max_retries}): {e}. "
                    f"Retrying in {current_delay}s..."
                )
                time.sleep(current_delay)
                current_delay *= self.backoff

        # Should never reach here, but just in case
        if last_exception is None:
            last_exception = Exception(
                f"{operation_name} failed without exception."
            )

        raise last_exception

    def publish_validation_request(
        self,
        routing_key: str,
        file_data: bytes,
        project_id: str,
        table_name: str,
        metadata: Metadata,
        task: ValidationTasks,
        insert: bool = False,
        insert_table_name: Optional[str] = None,
        insert_scheme: Optional[str] = None,
        insert_overwrite: Optional[bool] = None,
        insert_db_uri: Optional[str] = None,
        task_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        traceparent: Optional[str] = None,
        tracestate: Optional[str] = None,
        baggage: Optional[str] = None,
        **kwargs: str,
    ) -> str:
        """Publish a validation request message to the RabbitMQ exchange.

        Creates and sends a validation request message containing file data
        and metadata to be processed by validation workers. The file data
        is converted to hexadecimal format for safe JSON transmission.

        Args:
            routing_key (str): The routing key to route the message to the appropriate queue.
            file_data (bytes): Raw binary data of the file to be validated.
            project_id (str): Schema identifier to validate the file against.
            metadata (Metadata): Additional metadata including filename, priority, and
                other processing parameters.
            task (Validation Tasks): Task type for the validation request (e.g.,
                "sample_validation").
            insert (bool): Whether this validation request is for an insertion operation.
            insert_table_name (Optional[str]): If provided, indicates that the validation is for an insertion
                operation and specifies the target table name for the insertion.
            insert_overwrite (Optional[bool]): If True, indicates that the validation is for an overwrite
                operation.
            insert_db_uri (Optional[str]): If provided, indicates that the validation is for an insertion
                operation and specifies the database URI for the insertion.
            task_id (Optional[str]): Optional unique task ID (UUID) for tracking the validation request. If not provided, a new UUID will be generated.
            idempotency_key (Optional[str]): Optional idempotency key for ensuring idempotent processing of the validation request.
            traceparent (Optional[str]): W3C Trace Context traceparent header for distributed tracing.
            tracestate (Optional[str]): W3C Trace Context tracestate header for distributed tracing.
            baggage (Optional[str]): Baggage header for distributed context propagation.
            kwargs (str): Additional key-value pairs to include in the message.

        Returns:
            str: Unique task ID (UUID) for tracking the validation request.

        Message Format:
            Creates a ValidationMessage with the following structure:
            - id: Unique task identifier (UUID)
            - task: Task type (e.g., "sample_validation", "add_data")
            - file_data: Hexadecimal-encoded file content
            - project_id: Schema identifier for validation
            - metadata: Additional processing metadata
            - traceparent: W3C Trace Context traceparent header
            - tracestate: W3C Trace Context tracestate header
            - baggage: Baggage header for context propagation

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems.
        """

        if insert:
            if insert_overwrite is None:
                raise TypeError(
                    "insert_overwrite must be provided when insert is True"
                )
            if insert_db_uri is None:
                raise TypeError(
                    "insert_db_uri must be provided when insert is True"
                )

        def _publish() -> str:
            nonlocal task_id
            if task_id is None:
                task_id = str(uuid.uuid4())

            message = ValidationMessage(
                id=task_id,
                task=task,
                file_data=file_data.hex(),
                project_id=project_id,
                table_name=table_name,
                metadata=metadata,
                date=datetime.now().isoformat(),
                extra=kwargs,
                insert=insert,
                insert_table_name=insert_table_name,
                insert_scheme=insert_scheme,
                insert_overwrite=insert_overwrite,
                insert_db_uri=insert_db_uri,
                idempotency_key=idempotency_key,
                traceparent=traceparent,
                tracestate=tracestate,
                baggage=baggage,
            )

            self._channel.basic_publish(
                exchange=self.exchange_info["exchange"],
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    message_id=task_id,
                    timestamp=int(datetime.now().timestamp()),
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )

            return task_id

        return self._execute_with_retry(
            _publish,
            operation_name="publish_validation_request",
        )

    def publish_insertion_request(
        self,
        routing_key: str,
        file_data: bytes,
        project_id: str,
        metadata: Metadata,
        task: InsertionTasks,
        db_uri: str,
        table_name: str,
        scheme: Optional[str] = None,
        overwrite: bool = False,
        task_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        traceparent: Optional[str] = None,
        tracestate: Optional[str] = None,
        baggage: Optional[str] = None,
        **kwargs: str,
    ) -> str:
        """Publish an insertion request message to the RabbitMQ exchange.

        Creates and sends an insertion request message containing file data
        and metadata to be processed by insertion workers. The file data is converted to
        hexadecimal format for safe JSON transmission. The message includes an "overwrite"
        flag to indicate whether the insertion should overwrite to existing data or overwrite it.

        Args:
            routing_key (str): The routing key to route the message to the appropriate queue.
            file_data (bytes): Raw binary data of the file to be inserted.
            project_id (str): Schema identifier to insert the file against.
            metadata (Metadata): Additional metadata including filename, priority, and
                other processing parameters.
            task (InsertionTasks): Task type for the insertion request (e.g.,
                "sample_insertion").
            table_name (Optional[str]): Optional name of the target table for the insertion.
            scheme (Optional[str]): Optional name of the target schema for the insertion.
            overwrite (bool): Whether the insertion should overwrite to existing data (True) or overwrite it (False).
            db_uri (str): The URI for connecting to the database where the data should be inserted.
            task_id (Optional[str]): Optional unique task ID (UUID) for tracking the insertion request. If not provided, a new UUID will be generated.
            idempotency_key (Optional[str]): Optional idempotency key for ensuring idempotent processing of the insertion request.
            traceparent (Optional[str]): W3C Trace Context traceparent header for distributed tracing.
            tracestate (Optional[str]): W3C Trace Context tracestate header for distributed tracing.
            baggage (Optional[str]): Baggage header for distributed context propagation.
            kwargs (str): Additional key-value pairs to include in the message.
        """

        def _publish() -> str:
            nonlocal task_id
            if task_id is None:
                # actually, it is already str, but for type clarity
                task_id = str(uuid.uuid4())

            message = InsertionMessage(
                id=task_id,
                task=task,
                file_data=file_data.hex(),
                project_id=project_id,
                table_name=table_name,
                scheme=scheme,
                metadata=metadata,
                date=datetime.now().isoformat(),
                extra=kwargs,
                overwrite=overwrite,
                db_uri=db_uri,
                idempotency_key=idempotency_key,
                traceparent=traceparent,
                tracestate=tracestate,
                baggage=baggage,
            )

            self._channel.basic_publish(
                exchange=self.exchange_info["exchange"],
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    message_id=task_id,
                    timestamp=int(datetime.now().timestamp()),
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )

            return task_id

        return self._execute_with_retry(
            _publish,
            operation_name="publish_validation_request",
        )

    def close(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.close()
