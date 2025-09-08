from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PropertyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STRING: _ClassVar[PropertyType]
    INTEGER: _ClassVar[PropertyType]
    NUMBER: _ClassVar[PropertyType]
    BOOLEAN: _ClassVar[PropertyType]
STRING: PropertyType
INTEGER: PropertyType
NUMBER: PropertyType
BOOLEAN: PropertyType

class ApiResponse(_message.Message):
    __slots__ = ("status", "code", "message", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: str
    code: int
    message: str
    data: _containers.ScalarMap[str, str]
    def __init__(self, status: _Optional[str] = ..., code: _Optional[int] = ..., message: _Optional[str] = ..., data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Properties(_message.Message):
    __slots__ = ("type", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    type: PropertyType
    extra: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[_Union[PropertyType, str]] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class JsonSchema(_message.Message):
    __slots__ = ("schema", "type", "required", "properties")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Properties
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Properties, _Mapping]] = ...) -> None: ...
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    schema: str
    type: str
    required: _containers.RepeatedScalarFieldContainer[str]
    properties: _containers.MessageMap[str, Properties]
    def __init__(self, schema: _Optional[str] = ..., type: _Optional[str] = ..., required: _Optional[_Iterable[str]] = ..., properties: _Optional[_Mapping[str, Properties]] = ...) -> None: ...
