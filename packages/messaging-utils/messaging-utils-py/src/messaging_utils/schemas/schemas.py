from typing import Dict, Literal, TypedDict

from proto_utils.database.dtypes import JsonSchema

SchemasTasks = Literal["upload_schema", "remove_schema", "unknown"]


class SchemaMessage(TypedDict):
    id: str
    schema: JsonSchema
    import_name: str
    raw: bool
    tasks: SchemasTasks
    date: str
    extra: Dict[str, str]
