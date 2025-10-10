from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueueInfo(_message.Message):
    __slots__ = ("queue", "routing_key", "durable")
    QUEUE_FIELD_NUMBER: _ClassVar[int]
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    DURABLE_FIELD_NUMBER: _ClassVar[int]
    queue: str
    routing_key: str
    durable: bool
    def __init__(self, queue: _Optional[str] = ..., routing_key: _Optional[str] = ..., durable: bool = ...) -> None: ...

class ExchangeInfo(_message.Message):
    __slots__ = ("exchange", "type", "durable", "queues")
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DURABLE_FIELD_NUMBER: _ClassVar[int]
    QUEUES_FIELD_NUMBER: _ClassVar[int]
    exchange: str
    type: str
    durable: bool
    queues: _containers.RepeatedCompositeFieldContainer[QueueInfo]
    def __init__(self, exchange: _Optional[str] = ..., type: _Optional[str] = ..., durable: bool = ..., queues: _Optional[_Iterable[_Union[QueueInfo, _Mapping]]] = ...) -> None: ...
