from typing import Any, Dict, Literal, TypedDict

SchemasTasks = Literal["upload_schema", "remove_schema", "unknown"]


class SchemaMessage(TypedDict):
    id: str
    schema: Dict[str, Any]
    import_name: str
    raw: bool
    tasks: SchemasTasks
    date: str
    extra: Dict[str, str]
