from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RedisGetKeysRequest(_message.Message):
    __slots__ = ("pattern",)
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    def __init__(self, pattern: _Optional[str] = ...) -> None: ...

class RedisGetKeysResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, keys: _Optional[_Iterable[str]] = ...) -> None: ...

class RedisSetRequest(_message.Message):
    __slots__ = ("key", "value", "expiration")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    expiration: int
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ..., expiration: _Optional[int] = ...) -> None: ...

class RedisSetResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RedisGetRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class RedisGetResponse(_message.Message):
    __slots__ = ("value", "found")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    value: str
    found: bool
    def __init__(self, value: _Optional[str] = ..., found: bool = ...) -> None: ...

class RedisDeleteRequest(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, keys: _Optional[_Iterable[str]] = ...) -> None: ...

class RedisDeleteResponse(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class RedisPingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RedisPingResponse(_message.Message):
    __slots__ = ("pong",)
    PONG_FIELD_NUMBER: _ClassVar[int]
    pong: bool
    def __init__(self, pong: bool = ...) -> None: ...

class RedisGetCacheRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RedisGetCacheResponse(_message.Message):
    __slots__ = ("cache",)
    class CacheEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CACHE_FIELD_NUMBER: _ClassVar[int]
    cache: _containers.ScalarMap[str, str]
    def __init__(self, cache: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RedisClearCacheRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RedisClearCacheResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
