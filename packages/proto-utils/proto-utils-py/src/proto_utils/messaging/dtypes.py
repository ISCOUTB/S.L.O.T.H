from typing import Dict, Literal, TypedDict, List
from proto_utils.database.dtypes import JsonSchema

SchemasTasks = Literal["upload_schema", "remove_schema", "unknown"]
ValidationTasks = Literal["sample_validation", "unknown"]


class QueueInfo(TypedDict):
    queue: str
    durable: bool
    routing_key: str


class ExchangeInfo(TypedDict):
    exchange: str
    type: str
    durable: bool
    queues: List[QueueInfo]


class Metadata(TypedDict):
    filename: str
    content_type: str
    size: int


class GetRoutingKeySchemasRequest(TypedDict):
    pass


class GetRoutingKeyValidationsRequest(TypedDict):
    pass


class GetMessagingParamsRequest(TypedDict):
    pass


class GetMessagingParamsResponse(TypedDict):
    host: str
    port: int
    username: str
    password: str
    virtual_host: str
    exchange: ExchangeInfo


class RoutingKey(TypedDict):
    routing_key: str


class SchemaMessageRequest(TypedDict):
    pass


class SchemaMessageResponse(TypedDict):
    id: str
    schema: JsonSchema
    import_name: str
    raw: bool
    tasks: SchemasTasks
    date: str
    extra: Dict[str, str]


class ValidationMessageRequest(TypedDict):
    pass


class ValidationMessageResponse(TypedDict):
    id: str
    task: ValidationTasks
    file_data: str
    import_name: str
    metadata: Metadata
    date: str
    extra: Dict[str, str]
