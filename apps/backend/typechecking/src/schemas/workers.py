"""Worker Schemas Module.

This module defines TypedDict schemas for worker result messages
in the typechecking system. These schemas standardize the format
of results returned by validation and schema workers after processing
their respective message types.

The schemas ensure consistent result structure for downstream consumers
and provide proper typing for worker result handling and storage.
"""

from typing import TypedDict, Dict, Any
from pymongo.results import UpdateResult, InsertOneResult
from src.schemas.handlers import ValidationSummary, SummaryStatus


class DataValidated(TypedDict):
    """Data validation result schema.

    Represents the result of a file validation operation performed
    by validation workers. Contains the task identifier, completion
    status, and detailed validation results for further processing.

    Used by validation workers to report results back to the system
    and by result consumers to process validation outcomes.

    Attributes:
        task_id (str): Unique identifier linking back to the original validation request.
        status (SummaryStatus): Completion status - 'success' for successful validation,
            'failed' for validation processing errors.
        results (ValidationSummary): Detailed validation summary including statistics, status,
            and validation details from the ValidationSummary schema.

    Example:
        >>> result: DataValidated = {
        ...     "task_id": "550e8400-e29b-41d4-a716-446655440000",
        ...     "status": "success",
        ...     "results": {
        ...         "status": "success",
        ...         "summary": "All 100 records validated successfully",
        ...         "details": {
        ...             "total_items": 100,
        ...             "valid_items": 100,
        ...             "invalid_items": 0,
        ...             "error_count": 0,
        ...             "file_name": "data.csv",
        ...             "validated_at": "2024-01-15T10:30:00Z"
        ...         }
        ...     }
        ... }
    """

    task_id: str
    status: SummaryStatus
    results: ValidationSummary


class SchemaUpdated(TypedDict):
    """Schema update result schema.

    Represents the result of a schema creation or update operation
    performed by schema workers. Contains the task identifier,
    completion status, schema information, and database operation result.

    Used by schema workers to report schema update results back to
    the system and by result consumers to track schema changes.

    Attributes:
        task_id (str): Unique identifier linking back to the original schema update request.
        status (str): Completion status - 'completed' for successful schema update,
            'failed' for schema processing errors.
        schema (Dict[str, Any]): The complete JSON schema definition that was processed,
            including all validation rules, field types, and constraints.
        import_name (str): Schema identifier used for storage and retrieval.
        result (UpdateResult | InsertOneResult | None): MongoDB operation result from the database
            update/insert, None if the database operation failed or was not performed.

    Example:
        >>> result: SchemaUpdated = {
        ...     "task_id": "550e8400-e29b-41d4-a716-446655440001",
        ...     "status": "completed",
        ...     "schema": {
        ...         "type": "object",
        ...         "properties": {
        ...             "name": {"type": "string"},
        ...             "email": {"type": "string", "format": "email"}
        ...         },
        ...         "required": ["name", "email"]
        ...     },
        ...     "import_name": "user_profile_schema",
        ...     "result": UpdateResult(...)  # MongoDB operation result
        ... }
    """

    task_id: str
    status: str
    schema: Dict[str, Any]  # The updated JSON schema
    import_name: str
    result: UpdateResult | InsertOneResult | None
