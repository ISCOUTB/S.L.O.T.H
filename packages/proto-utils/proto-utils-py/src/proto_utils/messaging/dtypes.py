from typing import Dict, Literal, TypedDict
from proto_utils.database.dtypes import JsonSchema

SchemasTasks = Literal["upload_schema", "remove_schema", "unknown"]
ValidationTasks = Literal["sample_validation", "unknown"]


class Metadata(TypedDict):
    filename: str
    content_type: str
    size: int


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
