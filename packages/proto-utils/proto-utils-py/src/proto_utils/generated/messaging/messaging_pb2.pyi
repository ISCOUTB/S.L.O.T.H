from database import utils_pb2 as _utils_pb2
from messaging import validation_pb2 as _validation_pb2
from messaging import schemas_pb2 as _schemas_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SchemaMessageRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SchemaMessageResponse(_message.Message):
    __slots__ = ("id", "schema", "import_name", "raw", "task", "date", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    id: str
    schema: _utils_pb2.JsonSchema
    import_name: str
    raw: bool
    task: _schemas_pb2.SchemasTasks
    date: str
    extra: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., schema: _Optional[_Union[_utils_pb2.JsonSchema, _Mapping]] = ..., import_name: _Optional[str] = ..., raw: bool = ..., task: _Optional[_Union[_schemas_pb2.SchemasTasks, str]] = ..., date: _Optional[str] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ValidationMessageRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ValidationMessageResponse(_message.Message):
    __slots__ = ("id", "task", "file_data", "import_name", "date", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    id: str
    task: _validation_pb2.ValidationTasks
    file_data: str
    import_name: str
    date: str
    extra: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., task: _Optional[_Union[_validation_pb2.ValidationTasks, str]] = ..., file_data: _Optional[str] = ..., import_name: _Optional[str] = ..., date: _Optional[str] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...
