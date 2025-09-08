from proto_utils.generated.database import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MongoInsertOneSchemaRequest(_message.Message):
    __slots__ = ("import_name", "created_at", "active_schema", "schemas_releases")
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SCHEMAS_RELEASES_FIELD_NUMBER: _ClassVar[int]
    import_name: str
    created_at: str
    active_schema: _utils_pb2.JsonSchema
    schemas_releases: _containers.RepeatedCompositeFieldContainer[_utils_pb2.JsonSchema]
    def __init__(self, import_name: _Optional[str] = ..., created_at: _Optional[str] = ..., active_schema: _Optional[_Union[_utils_pb2.JsonSchema, _Mapping]] = ..., schemas_releases: _Optional[_Iterable[_Union[_utils_pb2.JsonSchema, _Mapping]]] = ...) -> None: ...

class MongoInsertOneSchemaResponse(_message.Message):
    __slots__ = ("result",)
    class ResultEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _containers.ScalarMap[str, str]
    def __init__(self, result: _Optional[_Mapping[str, str]] = ...) -> None: ...

class MongoCountAllDocumentsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MongoCountAllDocumentsResponse(_message.Message):
    __slots__ = ("amount",)
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    amount: int
    def __init__(self, amount: _Optional[int] = ...) -> None: ...

class MongoFindJsonSchemaRequest(_message.Message):
    __slots__ = ("import_name",)
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    import_name: str
    def __init__(self, import_name: _Optional[str] = ...) -> None: ...

class MongoFindJsonSchemaResponse(_message.Message):
    __slots__ = ("status", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    status: str
    extra: _containers.ScalarMap[str, str]
    def __init__(self, status: _Optional[str] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class MongoUpdateOneJsonSchemaRequest(_message.Message):
    __slots__ = ("import_name", "schema", "created_at")
    IMPORT_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    import_name: str
    schema: _utils_pb2.JsonSchema
    created_at: str
    def __init__(self, import_name: _Optional[str] = ..., schema: _Optional[_Union[_utils_pb2.JsonSchema, _Mapping]] = ..., created_at: _Optional[str] = ...) -> None: ...

class MongoUpdateOneJsonSchemaResponse(_message.Message):
    __slots__ = ("result",)
    class ResultEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _containers.ScalarMap[str, str]
    def __init__(self, result: _Optional[_Mapping[str, str]] = ...) -> None: ...
