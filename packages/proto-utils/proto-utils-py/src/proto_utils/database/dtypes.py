"""Database data types module.

This module contains TypedDict definitions for database operations including
Redis operations, JSON schema validation, and API response structures.
These types correspond to the Protocol Buffer message definitions.
"""

from typing import TypedDict, Dict, Literal, List, Optional


PropertyType = Literal["string", "integer", "number", "boolean"]
"""Type alias for supported property types in JSON schema validation.

Supported types:
    - string: Text/string values
    - integer: Whole number values  
    - number: Decimal/floating point values
    - boolean: True/false values
"""


class ApiResponse(TypedDict):
    """Standard API response structure used throughout the system.

    Provides consistent response format across all service operations.

    Attributes:
        status (str): The status of the response (e.g., "success", "error", "pending")
        code (int): The HTTP status code associated with the response (200, 404, 500, etc.)
        message (str): A descriptive message providing additional information about the response
        data (Dict[str, str]): The actual data returned in the response (key-value pairs)
    """

    status: str
    code: int
    message: str
    data: Dict[str, str]


class Properties(TypedDict):
    """Properties of a field in a JSON schema.

    Contains type information and additional metadata for schema validation.

    Attributes:
        type (PropertyType): The data type of this property
        extra (Dict[str, str]): Additional metadata or constraints for the property
    """

    type: PropertyType
    extra: Dict[str, str]


class JsonSchema(TypedDict):
    """JSON Schema definition for data validation and structure.

    Used to define the expected structure and types of JSON documents.

    Attributes:
        schema (str): The JSON schema version (e.g., "https://json-schema.org/draft/2020-12/schema")
        type (str): The root type of the schema (typically "object")
        required (List[str]): List of required field names
        properties (Dict[str, Properties]): Definition of all properties in the schema
    """

    schema: str
    type: str
    required: List[str]
    properties: Dict[str, Properties]


class RedisGetKeysRequest(TypedDict):
    """Request message for retrieving keys that match a specific pattern.

    Attributes:
        pattern (str): Pattern to match keys (e.g., "user:*", "session:*", "*:temp")
    """

    pattern: str


class RedisGetKeysResponse(TypedDict):
    """Response message containing all keys that match the requested pattern.

    Attributes:
        keys (List[str]): List of keys matching the pattern
    """

    keys: List[str]


class RedisSetRequest(TypedDict):
    """Request message for setting a key-value pair in Redis.

    Attributes:
        key (str): Key to set (must be non-empty)
        value (str): Value to associate with the key
        expiration (Optional[int]): Expiration time in seconds (optional)
    """

    key: str
    value: str
    expiration: Optional[int]


class RedisSetResponse(TypedDict):
    """Response message indicating the success of a SET operation.

    Attributes:
        success (bool): Indicates if the operation was successful
    """

    success: bool


class RedisGetRequest(TypedDict):
    """Request message for retrieving a value by its key.

    Attributes:
        key (str): Key to retrieve (must be non-empty)
    """

    key: str


class RedisGetResponse(TypedDict):
    """Response message containing the value associated with the requested key.

    Attributes:
        value (Optional[str]): Value associated with the key (None if key doesn't exist)
        found (bool): Indicates if the key was found in the database
    """

    value: Optional[str]
    found: bool


class RedisDeleteRequest(TypedDict):
    """Request message for deleting one or more keys from Redis.

    Attributes:
        keys (List[str]): List of keys to delete (can be empty list)
    """

    keys: List[str]


class RedisDeleteResponse(TypedDict):
    """Response message indicating how many keys were successfully deleted.

    Attributes:
        count (int): Number of keys that were actually deleted
    """

    count: int


class RedisPingRequest(TypedDict):
    """Request message for checking Redis server connectivity.

    No fields needed for ping operation.
    """

    pass


class RedisPingResponse(TypedDict):
    """Response message for ping operation.

    Attributes:
        pong (bool): Should always be true if the Redis server is reachable and responsive
    """

    pong: bool


class RedisGetCacheRequest(TypedDict):
    """Request message for retrieving the entire Redis cache.

    Warning: This operation can be expensive on large datasets.
    No fields needed for getting the entire cache.
    """

    pass


class RedisGetCacheResponse(TypedDict):
    """Response message containing all key-value pairs in the Redis cache.

    Attributes:
        cache (Dict[str, str]): Key-value pairs representing the entire cache contents
    """

    cache: Dict[str, str]


class RedisClearCacheRequest(TypedDict):
    """Request message for clearing all data from the Redis cache.

    Warning: This operation is irreversible and will delete all data.
    No fields needed for clearing the cache.
    """

    pass


class RedisClearCacheResponse(TypedDict):
    """Response message indicating the success of cache clearing operation.

    Attributes:
        success (bool): Indicates if the cache was successfully cleared
    """

    success: bool


class MongoInsertOneSchemaRequest(TypedDict):
    """Request message for inserting a new schema document into MongoDB.

    Used to store JSON schema definitions with version history.

    Attributes:
        import_name (str): Unique identifier for the schema (e.g., "user_table", "product_schema")
        created_at (str): ISO timestamp when the schema was created
        active_schema (JsonSchema): The currently active/latest version of the schema
        schemas_releases (List[JsonSchema]): Historical versions of the schema for versioning
    """

    import_name: str
    created_at: str
    active_schema: JsonSchema
    schemas_releases: List[JsonSchema]


class MongoInsertOneSchemaResponse(TypedDict):
    """Response message for schema insertion operation.

    Attributes:
        status (str): Status of the insertion operation ("inserted", "no_change", "error", "updated")
        result (Dict[str, str]): Generic result data from the insertion operation
    """

    status: Literal["inserted", "no_change", "error", "updated"]
    result: Dict[str, str]


class MongoCountAllDocumentsRequest(TypedDict):
    """Request message for counting all documents in a MongoDB collection.

    No fields needed for counting documents.
    """

    pass


class MongoCountAllDocumentsResponse(TypedDict):
    """Response message containing the total count of schema documents.

    Attributes:
        amount (int): Total number of schema documents in the collection
    """

    amount: int


class MongoFindJsonSchemaRequest(TypedDict):
    """Request message for finding a JSON schema by its import name.

    Attributes:
        import_name (str): The unique identifier of the schema to find
    """

    import_name: str


class MongoFindJsonSchemaResponse(TypedDict):
    """Response message containing the found schema information.

    Attributes:
        status (str): Status of the find operation ("found", "not_found", "error")
        extra (Dict[str, str]): Additional metadata or error information
        schema (Optional[JsonSchema]): The found schema definition (None if not found)
    """

    status: Literal["found", "not_found", "error"]
    extra: Dict[str, str]
    schema: Optional[JsonSchema]


class MongoUpdateOneJsonSchemaRequest(TypedDict):
    """Request message for updating an existing JSON schema.

    Used to modify schema definitions and add new versions.

    Attributes:
        import_name (str): Unique identifier of the schema to update
        schema (JsonSchema): The new schema definition to set as active
        created_at (str): ISO timestamp when this update was created
    """

    import_name: str
    schema: JsonSchema
    created_at: str


class MongoUpdateOneJsonSchemaResponse(TypedDict):
    """Response message for schema update operation.

    Attributes:
        status (str): Status of the update operation ("error", "no_change", "updated")
        result (Dict[str, str]): Generic result data from the update operation
    """

    status: Literal["error", "no_change", "updated"]
    result: Dict[str, str]


class MongoDeleteOneJsonSchemaRequest(TypedDict):
    """Request message for deleting a JSON schema by its import name.

    Attributes:
        import_name (str): The unique identifier of the schema to delete
    """

    import_name: str


class MongoDeleteOneJsonSchemaResponse(TypedDict):
    """Response message for schema deletion operation.

    Attributes:
        success (bool): Indicates if the deletion was successful
        message (str): Descriptive message about the operation result or any errors
        status (str): Status of the deletion operation ("deleted", "error", "reverted")
        extra (Dict[str, str]): Generic result data from the deletion operation
    """

    success: bool
    message: str
    status: Literal["deleted", "error", "reverted"]
    extra: Dict[str, str]


class MongoDeleteImportNameRequest(TypedDict):
    """Request message for deleting all schemas associated with a specific import name.

    Attributes:
        import_name (str): The unique identifier of the import name to delete
    """

    import_name: str


class MongoDeleteImportNameResponse(TypedDict):
    """Response message for import name deletion operation.

    Attributes:
        success (bool): Indicates if the deletion was successful
        message (str): Descriptive message about the operation result or any errors
        status (str): Status of the deletion operation ("deleted", "error")
        extra (Dict[str, str]): Generic result data from the deletion operation
    """

    success: bool
    message: str
    status: Literal["deleted", "error"]
    extra: Dict[str, str]


class UpdateTaskIdRequest(TypedDict):
    """Request message for updating an existing task's information.

    Attributes:
        task_id (str): Unique identifier of the task to update
        field (str): Specific field to update (e.g., "status", "progress", "error_message")
        value (str): New value for the specified field
        task (str): Task type/category identifier (e.g., "data_import", "schema_validation")
        message (Optional[str]): Optional descriptive message to log with the update
        data (Dict[str, str]): Additional data to merge with existing task data
        reset_data (Optional[bool]): If true, replace all existing data instead of merging (default: false)
    """

    task_id: str
    field: str
    value: str
    task: str
    message: Optional[str]
    data: Dict[str, str]
    reset_data: Optional[bool]


class UpdateTaskIdResponse(TypedDict):
    """Response message for task update operations.

    Attributes:
        success (bool): Indicates if the update operation was successful
        message (str): Descriptive message about the operation result or any errors
    """

    success: bool
    message: str


class SetTaskIdRequest(TypedDict):
    """Request message for creating or setting a new task entry.

    Attributes:
        task_id (str): Unique identifier for the new task
        value (ApiResponse): Complete task data encapsulated in ApiResponse format
        task (str): Task type/category under which the task is stored
    """

    task_id: str
    value: ApiResponse
    task: str


class SetTaskIdResponse(TypedDict):
    """Response message for task creation operations.

    Attributes:
        success (bool): Indicates if the task was successfully created/set
        message (str): Descriptive message about the operation result or any errors
    """

    success: bool
    message: str


class GetTaskIdRequest(TypedDict):
    """Request message for retrieving a specific task by its ID.

    Attributes:
        task_id (str): Unique identifier of the task to retrieve
        task (str): Task type/category to search within
    """

    task_id: str
    task: str


class GetTaskIdResponse(TypedDict):
    """Response message containing the requested task information.

    Attributes:
        value (Optional[ApiResponse]): Task data if found (None if not found)
        found (bool): Indicates whether the task was found in the database
    """

    value: Optional[ApiResponse]
    found: bool


class GetTasksByImportNameRequest(TypedDict):
    """Request message for finding all tasks associated with a specific import name.

    Useful for tracking all tasks related to a particular data import or schema.

    Attributes:
        import_name (str): The import identifier to filter tasks by
        task (str): Task type/category to search within
    """

    import_name: str
    task: str


class GetTasksByImportNameResponse(TypedDict):
    """Response message containing all tasks matching the import name criteria.

    Attributes:
        tasks (List[ApiResponse]): List of all matching tasks
    """

    tasks: List[ApiResponse]
