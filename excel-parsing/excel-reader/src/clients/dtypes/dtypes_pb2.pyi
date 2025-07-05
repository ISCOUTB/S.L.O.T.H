from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AstType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AST_UNKNOWN: _ClassVar[AstType]
    AST_BINARY_EXPRESSION: _ClassVar[AstType]
    AST_CELL_RANGE: _ClassVar[AstType]
    AST_FUNCTION: _ClassVar[AstType]
    AST_CELL: _ClassVar[AstType]
    AST_NUMBER: _ClassVar[AstType]
    AST_LOGICAL: _ClassVar[AstType]
    AST_TEXT: _ClassVar[AstType]

class RefType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REF_UNKNOWN: _ClassVar[RefType]
    REF_RELATIVE: _ClassVar[RefType]
    REF_ABSOLUTE: _ClassVar[RefType]
    REF_MIXED: _ClassVar[RefType]
AST_UNKNOWN: AstType
AST_BINARY_EXPRESSION: AstType
AST_CELL_RANGE: AstType
AST_FUNCTION: AstType
AST_CELL: AstType
AST_NUMBER: AstType
AST_LOGICAL: AstType
AST_TEXT: AstType
REF_UNKNOWN: RefType
REF_RELATIVE: RefType
REF_ABSOLUTE: RefType
REF_MIXED: RefType

class AST(_message.Message):
    __slots__ = ("type", "operator", "left", "right", "arguments", "name", "refType", "key", "number_value", "text_value", "logical_value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REFTYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    type: AstType
    operator: str
    left: AST
    right: AST
    arguments: _containers.RepeatedCompositeFieldContainer[AST]
    name: str
    refType: RefType
    key: str
    number_value: float
    text_value: str
    logical_value: bool
    def __init__(self, type: _Optional[_Union[AstType, str]] = ..., operator: _Optional[str] = ..., left: _Optional[_Union[AST, _Mapping]] = ..., right: _Optional[_Union[AST, _Mapping]] = ..., arguments: _Optional[_Iterable[_Union[AST, _Mapping]]] = ..., name: _Optional[str] = ..., refType: _Optional[_Union[RefType, str]] = ..., key: _Optional[str] = ..., number_value: _Optional[float] = ..., text_value: _Optional[str] = ..., logical_value: bool = ...) -> None: ...

class Tokens(_message.Message):
    __slots__ = ("tokens",)
    class Token(_message.Message):
        __slots__ = ("value", "type", "subtype")
        VALUE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        SUBTYPE_FIELD_NUMBER: _ClassVar[int]
        value: str
        type: str
        subtype: str
        def __init__(self, value: _Optional[str] = ..., type: _Optional[str] = ..., subtype: _Optional[str] = ...) -> None: ...
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[Tokens.Token]
    def __init__(self, tokens: _Optional[_Iterable[_Union[Tokens.Token, _Mapping]]] = ...) -> None: ...
