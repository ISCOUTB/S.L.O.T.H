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
from typing import Any, Callable, Dict, Optional, TypeVar

import pika
from pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    StreamLostError,
)

from messaging_utils.core.connection_params import messaging_params
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.schemas.connection import (
    AllConnectionParams,
    ConnectionParams,
    ExchangeInfo,
)
from messaging_utils.schemas.schemas import SchemaMessage, SchemasTasks
from messaging_utils.schemas.validation import (
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
                AllConnectionParams(**params, exchange=self.exchange_info)
            )

        self._channel = RabbitMQConnectionFactory.get_thread_channel()

    def _get_healthy_channel(
        self, force_new: bool = False
    ) -> pika.channel.Channel:
        """Get a healthy RabbitMQ channel.

        Ensures that the channel is open and the connection is healthy.
        If not, it retrieves a new channel from the factory connection.

        Args:
            force_new (bool): Force retrieval of a new channel.

        Returns:
            pika.channel.Channel: Healthy RabbitMQ channel.
        """
        if force_new or not self._channel or not self._channel.is_open:
            self._channel = RabbitMQConnectionFactory.get_thread_channel()
        return self._channel

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
        raise last_exception

    def publish_validation_request(
        self,
        routing_key: str,
        file_data: bytes,
        import_name: str,
        metadata: Metadata,
        task: ValidationTasks,
        **kwargs: str,
    ) -> str:
        """Publish a validation request message to the RabbitMQ exchange.

        Creates and sends a validation request message containing file data
        and metadata to be processed by validation workers. The file data
        is converted to hexadecimal format for safe JSON transmission.

        Args:
            routing_key (str): The routing key to route the message to the appropriate queue.
            file_data (bytes): Raw binary data of the file to be validated.
            import_name (str): Schema identifier to validate the file against.
            metadata (Metadata): Additional metadata including filename, priority, and
                other processing parameters.
            task (Validation Tasks): Task type for the validation request (e.g.,
                "sample_validation").
            kwargs (str): Additional key-value pairs to include in the message.

        Returns:
            str: Unique task ID (UUID) for tracking the validation request.

        Message Format:
            Creates a ValidationMessage with the following structure:
            - id: Unique task identifier (UUID)
            - task: Task type (e.g., "sample_validation", "add_data")
            - file_data: Hexadecimal-encoded file content
            - import_name: Schema identifier for validation
            - metadata: Additional processing metadata

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems.
        """

        def _publish() -> str:
            task_id = str(uuid.uuid4())

            message = ValidationMessage(
                id=task_id,
                task=task,
                file_data=file_data.hex(),
                import_name=import_name,
                metadata=metadata,
                date=datetime.now().isoformat(),
                extra=kwargs,
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

    def publish_schema_update(
        self,
        routing_key: str,
        schema: Dict[str, Any] = None,
        import_name: str = None,
        raw: bool = False,
        task: SchemasTasks = None,
        **kwargs: str,
    ) -> str:
        """Publish a schema update message to the RabbitMQ exchange.

        Creates and sends a schema update message containing schema definition
        and metadata to be processed by schema workers. The schema is stored
        and associated with the specified import name.

        Args:
            routing_key: The routing key to route the message to the appropriate queue.
            schema: Dictionary containing the schema definition with validation
                rules, field types, and constraints.
            import_name: Unique identifier for the schema to be created or updated.
            raw: Boolean flag indicating if the schema is in raw format
                requiring processing or is already processed.
            task: Task type for the schema operation (e.g., "upload_schema").
            kwargs: Additional key-value pairs to include in the message.

        Returns:
            str: Unique task ID (UUID) for tracking the schema update request.

        Message Format:
            Creates a SchemaMessage with the following structure:
            - id: Unique task identifier (UUID)
            - timestamp: ISO format timestamp of message creation
            - schema: Schema definition dictionary
            - import_name: Schema identifier for storage
            - raw: Flag indicating schema processing requirements

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems.
        """

        def _publish() -> str:
            task_id = str(uuid.uuid4())

            message = SchemaMessage(
                id=task_id,
                schema=schema,
                import_name=import_name,
                raw=raw,
                tasks=task,
                date=datetime.now().isoformat(),
                extra=kwargs,
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
            operation_name="publish_schema_update",
        )

    def close(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.close()
