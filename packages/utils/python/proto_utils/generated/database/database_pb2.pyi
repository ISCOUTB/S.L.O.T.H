from proto_utils.generated.database import utils_pb2 as _utils_pb2
from proto_utils.generated.database import redis_pb2 as _redis_pb2  # noqa: F401
from proto_utils.generated.database import mongo_pb2 as _mongo_pb2  # noqa: F401
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateTaskIdRequest(_message.Message):
    __slots__ = ("task_id", "field", "value", "task", "message", "data", "reset_data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    RESET_DATA_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    field: str
    value: str
    task: str
    message: str
    data: _containers.ScalarMap[str, str]
    reset_data: bool
    def __init__(self, task_id: _Optional[str] = ..., field: _Optional[str] = ..., value: _Optional[str] = ..., task: _Optional[str] = ..., message: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ..., reset_data: bool = ...) -> None: ...

class UpdateTaskIdResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class SetTaskIdRequest(_message.Message):
    __slots__ = ("task_id", "value", "task")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    value: _utils_pb2.ApiResponse
    task: str
    def __init__(self, task_id: _Optional[str] = ..., value: _Optional[_Union[_utils_pb2.ApiResponse, _Mapping]] = ..., task: _Optional[str] = ...) -> None: ...

class SetTaskIdResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetTaskIdRequest(_message.Message):
    __slots__ = ("task_id", "task")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    task: str
    def __init__(self, task_id: _Optional[str] = ..., task: _Optional[str] = ...) -> None: ...

class GetTaskIdResponse(_message.Message):
    __slots__ = ("value", "found")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    value: _utils_pb2.ApiResponse
    found: bool
    def __init__(self, value: _Optional[_Union[_utils_pb2.ApiResponse, _Mapping]] = ..., found: bool = ...) -> None: ...

class GetTasksByImportNameRequest(_message.Message):
    __slots__ = ("import_name", "task")
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    import_name: str
    task: str
    def __init__(self, import_name: _Optional[str] = ..., task: _Optional[str] = ...) -> None: ...

class GetTasksByImportNameResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[_utils_pb2.ApiResponse]
    def __init__(self, tasks: _Optional[_Iterable[_Union[_utils_pb2.ApiResponse, _Mapping]]] = ...) -> None: ...
