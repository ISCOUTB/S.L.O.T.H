from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ValidationTasks(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SAMPLE_VALIDATION: _ClassVar[ValidationTasks]
SAMPLE_VALIDATION: ValidationTasks

class Metadata(_message.Message):
    __slots__ = ("filename", "content_type", "size")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    filename: str
    content_type: str
    size: int
    def __init__(self, filename: _Optional[str] = ..., content_type: _Optional[str] = ..., size: _Optional[int] = ...) -> None: ...
