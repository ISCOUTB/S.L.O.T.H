from _typeshed import Incomplete
from typing import Literal, TypedDict

PropertyType: Incomplete

class ApiResponse(TypedDict):
    status: str
    code: int
    message: str
    data: dict[str, str]

class Properties(TypedDict):
    type: PropertyType
    extra: dict[str, str]

class JsonSchema(TypedDict):
    schema: str
    type: str
    required: list[str]
    properties: dict[str, Properties]

class RedisGetKeysRequest(TypedDict):
    pattern: str

class RedisGetKeysResponse(TypedDict):
    keys: list[str]

class RedisSetRequest(TypedDict):
    key: str
    value: str
    expiration: int | None

class RedisSetResponse(TypedDict):
    success: bool

class RedisGetRequest(TypedDict):
    key: str

class RedisGetResponse(TypedDict):
    value: str | None
    found: bool

class RedisDeleteRequest(TypedDict):
    keys: list[str]

class RedisDeleteResponse(TypedDict):
    count: int

class RedisPingRequest(TypedDict): ...

class RedisPingResponse(TypedDict):
    pong: bool

class RedisGetCacheRequest(TypedDict): ...

class RedisGetCacheResponse(TypedDict):
    cache: dict[str, str]

class RedisClearCacheRequest(TypedDict): ...

class RedisClearCacheResponse(TypedDict):
    success: bool

class MongoInsertOneSchemaRequest(TypedDict):
    import_name: str
    created_at: str
    active_schema: JsonSchema
    schemas_releases: list[JsonSchema]

class MongoInsertOneSchemaResponse(TypedDict):
    status: Literal['inserted', 'no_change', 'error', 'updated']
    result: dict[str, str]

class MongoCountAllDocumentsRequest(TypedDict): ...

class MongoCountAllDocumentsResponse(TypedDict):
    amount: int

class MongoFindJsonSchemaRequest(TypedDict):
    import_name: str

class MongoFindJsonSchemaResponse(TypedDict):
    status: Literal['found', 'not_found', 'error']
    extra: dict[str, str]
    schema: JsonSchema | None

class MongoUpdateOneJsonSchemaRequest(TypedDict):
    import_name: str
    schema: JsonSchema
    created_at: str

class MongoUpdateOneJsonSchemaResponse(TypedDict):
    status: Literal['error', 'no_change', 'updated']
    result: dict[str, str]

class MongoDeleteOneJsonSchemaRequest(TypedDict):
    import_name: str

class MongoDeleteOneJsonSchemaResponse(TypedDict):
    success: bool
    message: str
    status: Literal['deleted', 'error', 'reverted']
    extra: dict[str, str]

class MongoDeleteImportNameRequest(TypedDict):
    import_name: str

class MongoDeleteImportNameResponse(TypedDict):
    success: bool
    message: str
    status: Literal['deleted', 'error']
    extra: dict[str, str]

class UpdateTaskIdRequest(TypedDict):
    task_id: str
    field: str
    value: str
    task: str
    message: str | None
    data: dict[str, str]
    reset_data: bool | None

class UpdateTaskIdResponse(TypedDict):
    success: bool
    message: str

class SetTaskIdRequest(TypedDict):
    task_id: str
    value: ApiResponse
    task: str

class SetTaskIdResponse(TypedDict):
    success: bool
    message: str

class GetTaskIdRequest(TypedDict):
    task_id: str
    task: str

class GetTaskIdResponse(TypedDict):
    value: ApiResponse | None
    found: bool

class GetTasksByImportNameRequest(TypedDict):
    import_name: str
    task: str

class GetTasksByImportNameResponse(TypedDict):
    tasks: list[ApiResponse]
