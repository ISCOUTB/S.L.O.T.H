from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SchemasTasks(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[SchemasTasks]
    UPLOAD_SCHEMA: _ClassVar[SchemasTasks]
    REMOVE_SCHEMA: _ClassVar[SchemasTasks]
UNKNOWN: SchemasTasks
UPLOAD_SCHEMA: SchemasTasks
REMOVE_SCHEMA: SchemasTasks
