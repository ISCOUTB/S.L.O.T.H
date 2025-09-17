from parsers import ddl_generator_pb2 as _ddl_generator_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BuildSQLRequest(_message.Message):
    __slots__ = ("cols", "dtypes", "table_name")
    class ColumnInfo(_message.Message):
        __slots__ = ("type", "extra")
        TYPE_FIELD_NUMBER: _ClassVar[int]
        EXTRA_FIELD_NUMBER: _ClassVar[int]
        type: str
        extra: str
        def __init__(self, type: _Optional[str] = ..., extra: _Optional[str] = ...) -> None: ...
    class ColsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _ddl_generator_pb2.DDLResponse
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_ddl_generator_pb2.DDLResponse, _Mapping]] = ...) -> None: ...
    class DtypesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: BuildSQLRequest.ColumnInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BuildSQLRequest.ColumnInfo, _Mapping]] = ...) -> None: ...
    COLS_FIELD_NUMBER: _ClassVar[int]
    DTYPES_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    cols: _containers.MessageMap[str, _ddl_generator_pb2.DDLResponse]
    dtypes: _containers.MessageMap[str, BuildSQLRequest.ColumnInfo]
    table_name: str
    def __init__(self, cols: _Optional[_Mapping[str, _ddl_generator_pb2.DDLResponse]] = ..., dtypes: _Optional[_Mapping[str, BuildSQLRequest.ColumnInfo]] = ..., table_name: _Optional[str] = ...) -> None: ...

class BuildSQLResponse(_message.Message):
    __slots__ = ("content", "error")
    class SQLContent(_message.Message):
        __slots__ = ("sql", "columns")
        SQL_FIELD_NUMBER: _ClassVar[int]
        COLUMNS_FIELD_NUMBER: _ClassVar[int]
        sql: str
        columns: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, sql: _Optional[str] = ..., columns: _Optional[_Iterable[str]] = ...) -> None: ...
    class Content(_message.Message):
        __slots__ = ("sql_content",)
        SQL_CONTENT_FIELD_NUMBER: _ClassVar[int]
        sql_content: _containers.RepeatedCompositeFieldContainer[BuildSQLResponse.SQLContent]
        def __init__(self, sql_content: _Optional[_Iterable[_Union[BuildSQLResponse.SQLContent, _Mapping]]] = ...) -> None: ...
    class ContentEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: BuildSQLResponse.Content
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[BuildSQLResponse.Content, _Mapping]] = ...) -> None: ...
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    content: _containers.MessageMap[int, BuildSQLResponse.Content]
    error: str
    def __init__(self, content: _Optional[_Mapping[int, BuildSQLResponse.Content]] = ..., error: _Optional[str] = ...) -> None: ...
