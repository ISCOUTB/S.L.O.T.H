"""Message Publishers Module.

This module provides publishers for sending messages to RabbitMQ queues
in the typechecking system. The publishers handle message formatting,
routing, and delivery properties for validation and schema update operations.

Publishers use the factory RabbitMQ connection and handle message
serialization, unique ID generation, and proper message properties
for reliable delivery and processing.

Example:
    Publishing validation requests:

    >>> from src.messaging.publishers import ValidationPublisher
    >>> publisher = ValidationPublisher()
    >>> task_id = publisher.publish_validation_request(
    ...     file_data=b"csv,data,here",
    ...     import_name="user_data",
    ...     metadata={"filename": "users.csv", "priority": 3},
    ...     task="sample_validation"
    ... )
    >>> print(f"Validation task ID: {task_id}")
"""

import json
import uuid
from typing import Any, Dict
from datetime import datetime

import pika
from src.messaging.connection_factory import RabbitMQConnectionFactory
from src.schemas.messaging import (
    ValidationMessage,
    SchemaMessage,
    SchemasTasks,
    ValidationTasks,
)


class ValidationPublisher:
    """Publisher for validation messages.

    This publisher handles sending validation requests and schema updates
    to the RabbitMQ exchange. It manages message formatting, unique ID
    generation, and proper message properties for reliable delivery.

    The publisher uses the Factory RabbitMQ connection and formats
    messages according to the defined message schemas with appropriate
    routing keys for proper queue distribution.

    Attributes:
        _channel: RabbitMQ channel obtained from the factory connection.
    """

    def __init__(self):
        """Initialize the ValidationPublisher.

        Sets up the publisher with a channel from the factory RabbitMQ
        connection. The channel is used for all message publishing operations.
        """
        self._channel = RabbitMQConnectionFactory.get_thread_channel()

    def publish_validation_request(
        self,
        file_data: bytes,
        import_name: str,
        metadata: Dict[str, Any],
        task: ValidationTasks,
    ) -> str:
        """Publish a validation request message to the RabbitMQ exchange.

        Creates and sends a validation request message containing file data
        and metadata to be processed by validation workers. The file data
        is converted to hexadecimal format for safe JSON transmission.

        Args:
            file_data: Raw binary data of the file to be validated.
            import_name: Schema identifier to validate the file against.
            metadata: Additional metadata including filename, priority, and
                other processing parameters.

        Returns:
            str: Unique task ID (UUID) for tracking the validation request.

        Message Format:
            Creates a ValidationMessage with the following structure:
            - id: Unique task identifier (UUID)
            - task: Task type (e.g., "sample_validation", "add_data")
            - timestamp: ISO format timestamp of message creation
            - file_data: Hexadecimal-encoded file content
            - import_name: Schema identifier for validation
            - metadata: Additional processing metadata
            - priority: Message priority (1-10, default from metadata or 5)

        Routing:
            Messages are sent to 'typechecking.exchange' with routing key
            'validation.request' and will be routed to validation workers.

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems.
        """
        task_id = str(uuid.uuid4())

        message: ValidationMessage = {
            "id": task_id,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "file_data": file_data.hex(),
            "import_name": import_name,
            "metadata": metadata,
            "priority": metadata.get("priority", 5),
            "date": datetime.now().isoformat(),
        }

        self._channel.basic_publish(
            exchange="typechecking.exchange",
            routing_key="validation.request",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                message_id=task_id,
                timestamp=int(datetime.now().timestamp()),
                delivery_mode=pika.DeliveryMode.Persistent,
                priority=message["priority"],
            ),
        )

        return task_id

    def publish_schema_update(
        self,
        schema: Dict = None,
        import_name: str = None,
        raw: bool = False,
        task: SchemasTasks = None,
    ) -> str:
        """Publish a schema update message to the RabbitMQ exchange.

        Creates and sends a schema update message containing schema definition
        and metadata to be processed by schema workers. The schema is stored
        and associated with the specified import name.

        Args:
            schema: Dictionary containing the schema definition with validation
                rules, field types, and constraints.
            import_name: Unique identifier for the schema to be created or updated.
            raw: Boolean flag indicating if the schema is in raw format
                requiring processing or is already processed.

        Returns:
            str: Unique task ID (UUID) for tracking the schema update request.

        Message Format:
            Creates a SchemaMessage with the following structure:
            - id: Unique task identifier (UUID)
            - timestamp: ISO format timestamp of message creation
            - schema: Schema definition dictionary
            - import_name: Schema identifier for storage
            - raw: Flag indicating schema processing requirements

        Routing:
            Messages are sent to 'typechecking.exchange' with routing key
            'schema.update' and will be routed to schema workers.

        Raises:
            Exception: If message publishing fails due to connection issues
                or serialization problems.
        """
        task_id = str(uuid.uuid4())

        message: SchemaMessage = {
            "id": task_id,
            "timestamp": datetime.now().isoformat(),
            "schema": schema,
            "import_name": import_name,
            "raw": raw,
            "task": task,
            "date": datetime.now().isoformat(),
        }

        self._channel.basic_publish(
            exchange="typechecking.exchange",
            routing_key="schema.update",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                message_id=task_id,
                timestamp=int(datetime.now().timestamp()),
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )

        return task_id
