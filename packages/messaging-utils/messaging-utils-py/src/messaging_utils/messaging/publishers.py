"""Message Publishers Module.

This module provides publishers for sending messages to RabbitMQ queues
in the typechecking system. The publishers handle message formatting,
routing, and delivery properties for validation and schema update operations.

Publishers use the factory RabbitMQ connection and handle message
serialization, unique ID generation, and proper message properties
for reliable delivery and processing.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import pika
from proto_utils.messaging.dtypes import (
    ExchangeInfo,
    GetMessagingParamsResponse,
    Metadata,
    SchemaMessageResponse,
    SchemasTasks,
    ValidationMessageResponse,
    ValidationTasks,
)

from messaging_utils.core.connection_params import messaging_params
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.schemas.connection import ConnectionParams


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
        *_: Any,
        **__: Any,
    ) -> None:
        """Initialize the Publisher.

        Sets up the publisher with a channel from the factory RabbitMQ
        connection. The channel is used for all message publishing operations.
        """
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
                GetMessagingParamsResponse(
                    **params, exchange=self.exchange_info
                )
            )

        self._channel = RabbitMQConnectionFactory.get_thread_channel()

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
            routing_key: The routing key to route the message to the appropriate queue.
            file_data: Raw binary data of the file to be validated.
            import_name: Schema identifier to validate the file against.
            metadata: Additional metadata including filename, priority, and
                other processing parameters.
            task: Task type for the validation request (e.g., "sample_validation").
            kwargs: Additional key-value pairs to include in the message.

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
        task_id = str(uuid.uuid4())

        message = ValidationMessageResponse(
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
        task_id = str(uuid.uuid4())

        message = SchemaMessageResponse(
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

    def close(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.close()
