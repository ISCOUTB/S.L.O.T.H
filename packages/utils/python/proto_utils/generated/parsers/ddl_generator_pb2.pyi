from proto_utils.generated.parsers import dtypes_pb2 as _dtypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DDLRequest(_message.Message):
    __slots__ = ("ast", "columns")
    class ColumnsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    AST_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ast: _dtypes_pb2.AST
    columns: _containers.ScalarMap[str, str]
    def __init__(self, ast: _Optional[_Union[_dtypes_pb2.AST, _Mapping]] = ..., columns: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DDLResponse(_message.Message):
    __slots__ = ("type", "sql", "number_value", "text_value", "logical_value", "cell", "refType", "column", "eror", "start", "end", "cells", "columns", "error", "operator", "left", "right", "name", "arguments", "operand")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    CELL_FIELD_NUMBER: _ClassVar[int]
    REFTYPE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    EROR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    CELLS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    OPERAND_FIELD_NUMBER: _ClassVar[int]
    type: _dtypes_pb2.AstType
    sql: str
    number_value: float
    text_value: str
    logical_value: bool
    cell: str
    refType: _dtypes_pb2.RefType
    column: str
    eror: str
    start: str
    end: str
    cells: _containers.RepeatedScalarFieldContainer[str]
    columns: _containers.RepeatedScalarFieldContainer[str]
    error: str
    operator: str
    left: DDLResponse
    right: DDLResponse
    name: str
    arguments: _containers.RepeatedCompositeFieldContainer[DDLResponse]
    operand: DDLResponse
    def __init__(self, type: _Optional[_Union[_dtypes_pb2.AstType, str]] = ..., sql: _Optional[str] = ..., number_value: _Optional[float] = ..., text_value: _Optional[str] = ..., logical_value: bool = ..., cell: _Optional[str] = ..., refType: _Optional[_Union[_dtypes_pb2.RefType, str]] = ..., column: _Optional[str] = ..., eror: _Optional[str] = ..., start: _Optional[str] = ..., end: _Optional[str] = ..., cells: _Optional[_Iterable[str]] = ..., columns: _Optional[_Iterable[str]] = ..., error: _Optional[str] = ..., operator: _Optional[str] = ..., left: _Optional[_Union[DDLResponse, _Mapping]] = ..., right: _Optional[_Union[DDLResponse, _Mapping]] = ..., name: _Optional[str] = ..., arguments: _Optional[_Iterable[_Union[DDLResponse, _Mapping]]] = ..., operand: _Optional[_Union[DDLResponse, _Mapping]] = ...) -> None: ...
