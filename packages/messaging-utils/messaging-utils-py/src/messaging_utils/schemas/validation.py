from typing import Dict, Literal, TypedDict

ValidationTasks = Literal["sample_validation", "unknown"]


class Metadata(TypedDict):
    filename: str
    content_type: str
    size: int


class ValidationMessage(TypedDict):
    id: str
    task: ValidationTasks
    file_data: str
    import_name: str
    metadata: Metadata
    date: str
    extra: Dict[str, str]
