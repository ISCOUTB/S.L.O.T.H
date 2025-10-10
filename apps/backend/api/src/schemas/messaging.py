"""Messaging Schemas Module.

This module defines TypedDict schemas for RabbitMQ message formats
used in the typechecking system. These schemas ensure consistent
message structure for validation requests and schema updates across
the distributed worker system.

The schemas define the contract between message publishers and consumers,
ensuring reliable message processing and proper data serialization.
"""

from typing import TypedDict, Literal


ValidationTasks = Literal["sample_validation"]
SchemasTasks = Literal["upload_schema", "remove_schema"]


class ValidationMessage(TypedDict):
    """Validation request message schema.

    Represents a message sent to validation workers for processing
    file validation requests. Contains all necessary information
    for workers to validate files against specified schemas.

    The file data is hex-encoded for safe transmission through JSON
    message serialization, and metadata provides additional context
    for processing priorities and options.

    Attributes:
        id: Unique identifier (UUID) for tracking the validation request.
        task: Task type. This can be for sample validation or adding new data.
        timestamp: ISO format timestamp of when the message was created.
        file_data: Hexadecimal-encoded binary file content for validation.
        import_name: Schema identifier to validate the file against.
        metadata: Additional context including filename, processing options,
            and other request-specific information.
        priority: Message priority level (1-10) for queue processing order.
      date: Date of the message creation in ISO format.

    Example:
        >>> message: ValidationMessage = {
        ...     "id": "550e8400-e29b-41d4-a716-446655440000",
        ...     "timestamp": "2024-01-15T10:30:00.000Z",
        ...     "file_data": "48656c6c6f2c576f726c64",  # "Hello,World" in hex
        ...     "import_name": "user_schema",
        ...     "metadata": {"filename": "users.csv", "format": "csv"},
        ...     "priority": 5
        ... }
    """

    id: str
    task: ValidationTasks
    timestamp: str
    file_data: str  # Hex-encoded file data
    import_name: str
    metadata: dict  # Additional metadata for the request
    priority: int  # Priority of the request
    date: str


class SchemaMessage(TypedDict):
    """Schema update message schema.

    Represents a message sent to schema workers for creating or
    updating schema definitions. Contains the schema definition
    and associated metadata for proper storage and indexing.

    Schema messages are used to maintain the schema registry
    that validation workers use to validate incoming files.

    Attributes:
        id: Unique identifier (UUID) for tracking the schema update request.
        task: Task type, this can be used for uploading schemas or removing them.
        timestamp: ISO format timestamp of when the message was created.
        schema: JSON schema definition containing validation rules,
            field types, constraints, and other schema metadata.
        import_name: Unique identifier for the schema used for storage
            and retrieval operations.
        raw: Boolean flag indicating if the schema is raw.
        date: Date of the message creation in ISO format.

    Example:
        >>> message: SchemaMessage = {
        ...     "id": "550e8400-e29b-41d4-a716-446655440001",
        ...     "timestamp": "2024-01-15T10:30:00.000Z",
        ...     "schema": {
        ...         "type": "object",
        ...         "properties": {
        ...             "name": {"type": "string"},
        ...             "age": {"type": "integer", "minimum": 0}
        ...         },
        ...         "required": ["name", "age"]
        ...     },
        ...     "import_name": "person_schema",
        ...     "raw": False
        ... }
    """

    id: str
    task: SchemasTasks
    timestamp: str
    schema: dict  # The JSON schema to be updated
    import_name: str  # The name of the import associated with the schema
    raw: bool = False  # Flag to indicate if the schema is raw or processed
    date: str  # Optional date field for additional context
