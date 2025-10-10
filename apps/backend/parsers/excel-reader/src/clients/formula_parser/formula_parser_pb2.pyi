import dtypes_pb2 as _dtypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FormulaParserRequest(_message.Message):
    __slots__ = ("formula",)
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    formula: str
    def __init__(self, formula: _Optional[str] = ...) -> None: ...

class FormulaParserResponse(_message.Message):
    __slots__ = ("formula", "tokens", "ast", "error")
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    AST_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    formula: str
    tokens: _dtypes_pb2.Tokens
    ast: _dtypes_pb2.AST
    error: str
    def __init__(self, formula: _Optional[str] = ..., tokens: _Optional[_Union[_dtypes_pb2.Tokens, _Mapping]] = ..., ast: _Optional[_Union[_dtypes_pb2.AST, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...
