"""Redis serialization and deserialization module.

This module provides serialization and deserialization utilities for Redis operations
including key-value storage, retrieval, deletion, and cache management functionality.
Contains the RedisSerde class with methods for converting between Python dictionaries
and Protocol Buffer messages for Redis operations.
"""

from proto_utils.database import dtypes
from proto_utils.generated.database import redis_pb2


class RedisSerde:
    """Serialization and deserialization utilities for Redis operations.

    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    Redis operations. Includes methods for general-purpose Redis operations
    and cache management functionality.
    """

    @staticmethod
    def serialize_get_keys_request(
        request: dtypes.RedisGetKeysRequest,
    ) -> redis_pb2.RedisGetKeysRequest:
        """Serialize a RedisGetKeysRequest dictionary to Protocol Buffer format.

        Args:
            request: The Redis get keys request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisGetKeysRequest message.
        """
        return redis_pb2.RedisGetKeysRequest(pattern=request["pattern"])

    @staticmethod
    def deserialize_get_keys_request(
        proto: redis_pb2.RedisGetKeysRequest,
    ) -> dtypes.RedisGetKeysRequest:
        """Deserialize a Protocol Buffer RedisGetKeysRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetKeysRequest message to deserialize.

        Returns:
            The deserialized Redis get keys request dictionary.
        """
        return dtypes.RedisGetKeysRequest(pattern=proto.pattern)

    @staticmethod
    def serialize_get_keys_response(
        response: dtypes.RedisGetKeysResponse,
    ) -> redis_pb2.RedisGetKeysResponse:
        """Serialize a RedisGetKeysResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis get keys response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisGetKeysResponse message.
        """
        return redis_pb2.RedisGetKeysResponse(keys=response["keys"])

    @staticmethod
    def deserialize_get_keys_response(
        proto: redis_pb2.RedisGetKeysResponse,
    ) -> dtypes.RedisGetKeysResponse:
        """Deserialize a Protocol Buffer RedisGetKeysResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetKeysResponse message to deserialize.

        Returns:
            The deserialized Redis get keys response dictionary.
        """
        return dtypes.RedisGetKeysResponse(keys=list(proto.keys))

    @staticmethod
    def serialize_set_request(
        request: dtypes.RedisSetRequest,
    ) -> redis_pb2.RedisSetRequest:
        """Serialize a RedisSetRequest dictionary to Protocol Buffer format.

        Args:
            request: The Redis set request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisSetRequest message.
        """
        return redis_pb2.RedisSetRequest(
            key=request["key"],
            value=request["value"],
            expiration=request["expiration"],
        )

    @staticmethod
    def deserialize_set_request(
        proto: redis_pb2.RedisSetRequest,
    ) -> dtypes.RedisSetRequest:
        """Deserialize a Protocol Buffer RedisSetRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisSetRequest message to deserialize.

        Returns:
            The deserialized Redis set request dictionary.
        """
        return dtypes.RedisSetRequest(
            key=proto.key,
            value=proto.value,
            expiration=proto.expiration if proto.HasField("expiration") else None,
        )

    @staticmethod
    def serialize_set_response(
        response: dtypes.RedisSetResponse,
    ) -> redis_pb2.RedisSetResponse:
        """Serialize a RedisSetResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis set response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisSetResponse message.
        """
        return redis_pb2.RedisSetResponse(success=response["success"])

    @staticmethod
    def deserialize_set_response(
        proto: redis_pb2.RedisSetResponse,
    ) -> dtypes.RedisSetResponse:
        """Deserialize a Protocol Buffer RedisSetResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisSetResponse message to deserialize.

        Returns:
            The deserialized Redis set response dictionary.
        """
        return dtypes.RedisSetResponse(success=proto.success)

    @staticmethod
    def serialize_get_request(
        request: dtypes.RedisGetRequest,
    ) -> redis_pb2.RedisGetRequest:
        """Serialize a RedisGetRequest dictionary to Protocol Buffer format.

        Args:
            request: The Redis get request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisGetRequest message.
        """
        return redis_pb2.RedisGetRequest(key=request["key"])

    @staticmethod
    def deserialize_get_request(
        proto: redis_pb2.RedisGetRequest,
    ) -> dtypes.RedisGetRequest:
        """Deserialize a Protocol Buffer RedisGetRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetRequest message to deserialize.

        Returns:
            The deserialized Redis get request dictionary.
        """
        return dtypes.RedisGetRequest(key=proto.key)

    @staticmethod
    def serialize_get_response(
        response: dtypes.RedisGetResponse,
    ) -> redis_pb2.RedisGetResponse:
        """Serialize a RedisGetResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis get response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisGetResponse message.
        """
        return redis_pb2.RedisGetResponse(
            value=response["value"],
            found=response["found"],
        )

    @staticmethod
    def deserialize_get_response(
        proto: redis_pb2.RedisGetResponse,
    ) -> dtypes.RedisGetResponse:
        """Deserialize a Protocol Buffer RedisGetResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetResponse message to deserialize.

        Returns:
            The deserialized Redis get response dictionary.
        """
        return dtypes.RedisGetResponse(
            value=proto.value if proto.HasField("value") else None,
            found=proto.found,
        )

    @staticmethod
    def serialize_delete_request(
        request: dtypes.RedisDeleteRequest,
    ) -> redis_pb2.RedisDeleteRequest:
        """Serialize a RedisDeleteRequest dictionary to Protocol Buffer format.

        Args:
            request: The Redis delete request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisDeleteRequest message.
        """
        return redis_pb2.RedisDeleteRequest(keys=request["keys"])

    @staticmethod
    def deserialize_delete_request(
        proto: redis_pb2.RedisDeleteRequest,
    ) -> dtypes.RedisDeleteRequest:
        """Deserialize a Protocol Buffer RedisDeleteRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisDeleteRequest message to deserialize.

        Returns:
            The deserialized Redis delete request dictionary.
        """
        return dtypes.RedisDeleteRequest(keys=list(proto.keys))

    @staticmethod
    def serialize_delete_response(
        response: dtypes.RedisDeleteResponse,
    ) -> redis_pb2.RedisDeleteResponse:
        """Serialize a RedisDeleteResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis delete response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisDeleteResponse message.
        """
        return redis_pb2.RedisDeleteResponse(count=response["count"])

    @staticmethod
    def deserialize_delete_response(
        proto: redis_pb2.RedisDeleteResponse,
    ) -> dtypes.RedisDeleteResponse:
        """Deserialize a Protocol Buffer RedisDeleteResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisDeleteResponse message to deserialize.

        Returns:
            The deserialized Redis delete response dictionary.
        """
        return dtypes.RedisDeleteResponse(count=proto.count)

    @staticmethod
    def serialize_ping_request(
        request: dtypes.RedisPingRequest = None,
    ) -> redis_pb2.RedisPingRequest:
        """Serialize a RedisPingRequest dictionary to Protocol Buffer format.

        Args:
            request: The Redis ping request dictionary to serialize (optional).

        Returns:
            The serialized Protocol Buffer RedisPingRequest message.
        """
        return redis_pb2.RedisPingRequest()

    @staticmethod
    def deserialize_ping_request(
        proto: redis_pb2.RedisPingRequest,
    ) -> dtypes.RedisPingRequest:
        """Deserialize a Protocol Buffer RedisPingRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisPingRequest message to deserialize.

        Returns:
            The deserialized Redis ping request dictionary.
        """
        return dtypes.RedisPingRequest

    @staticmethod
    def serialize_ping_response(
        response: dtypes.RedisPingResponse,
    ) -> redis_pb2.RedisPingResponse:
        """Serialize a RedisPingResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis ping response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisPingResponse message.
        """
        return redis_pb2.RedisPingResponse(pong=response["pong"])

    @staticmethod
    def deserialize_ping_response(
        proto: redis_pb2.RedisPingResponse,
    ) -> dtypes.RedisPingResponse:
        """Deserialize a Protocol Buffer RedisPingResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisPingResponse message to deserialize.

        Returns:
            The deserialized Redis ping response dictionary.
        """
        return dtypes.RedisPingResponse(pong=proto.pong)

    @staticmethod
    def serialize_get_cache_request(
        request: dtypes.RedisGetCacheRequest = None,
    ) -> redis_pb2.RedisGetCacheRequest:
        """Serialize a RedisGetCacheRequest dictionary to Protocol Buffer format.

        Warning: This operation can be expensive on large datasets.

        Args:
            request: The Redis get cache request dictionary to serialize (optional).

        Returns:
            The serialized Protocol Buffer RedisGetCacheRequest message.
        """
        return redis_pb2.RedisGetCacheRequest()

    @staticmethod
    def deserialize_get_cache_request(
        proto: redis_pb2.RedisGetCacheRequest,
    ) -> dtypes.RedisGetCacheRequest:
        """Deserialize a Protocol Buffer RedisGetCacheRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetCacheRequest message to deserialize.

        Returns:
            The deserialized Redis get cache request dictionary.
        """
        return dtypes.RedisClearCacheRequest()

    @staticmethod
    def serialize_get_cache_response(
        response: dtypes.RedisGetCacheResponse,
    ) -> redis_pb2.RedisGetCacheResponse:
        """Serialize a RedisGetCacheResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis get cache response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisGetCacheResponse message.
        """
        return redis_pb2.RedisGetCacheResponse(cache=response["cache"])

    @staticmethod
    def deserialize_get_cache_response(
        proto: redis_pb2.RedisGetCacheResponse,
    ) -> dtypes.RedisGetCacheResponse:
        """Deserialize a Protocol Buffer RedisGetCacheResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisGetCacheResponse message to deserialize.

        Returns:
            The deserialized Redis get cache response dictionary.
        """
        return dtypes.RedisGetCacheResponse(cache=dict(proto.cache))

    @staticmethod
    def serialize_clear_cache_request(
        request: dtypes.RedisClearCacheRequest = None,
    ) -> redis_pb2.RedisClearCacheRequest:
        """Serialize a RedisClearCacheRequest dictionary to Protocol Buffer format.

        Warning: This operation is irreversible and will delete all data.

        Args:
            request: The Redis clear cache request dictionary to serialize (optional).

        Returns:
            The serialized Protocol Buffer RedisClearCacheRequest message.
        """
        return redis_pb2.RedisClearCacheRequest()

    @staticmethod
    def deserialize_clear_cache_request(
        proto: redis_pb2.RedisClearCacheRequest,
    ) -> dtypes.RedisClearCacheRequest:
        """Deserialize a Protocol Buffer RedisClearCacheRequest to dictionary format.

        Args:
            proto: The Protocol Buffer RedisClearCacheRequest message to deserialize.

        Returns:
            The deserialized Redis clear cache request dictionary.
        """
        return dtypes.RedisClearCacheRequest()

    @staticmethod
    def serialize_clear_cache_response(
        response: dtypes.RedisClearCacheResponse,
    ) -> redis_pb2.RedisClearCacheResponse:
        """Serialize a RedisClearCacheResponse dictionary to Protocol Buffer format.

        Args:
            response: The Redis clear cache response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer RedisClearCacheResponse message.
        """
        return redis_pb2.RedisClearCacheResponse(success=response["success"])
    
    @staticmethod
    def deserialize_clear_cache_response(
        proto: redis_pb2.RedisClearCacheResponse,
    ) -> dtypes.RedisClearCacheResponse:
        """Deserialize a Protocol Buffer RedisClearCacheResponse to dictionary format.

        Args:
            proto: The Protocol Buffer RedisClearCacheResponse message to deserialize.

        Returns:
            The deserialized Redis clear cache response dictionary.
        """
        return dtypes.RedisClearCacheResponse(success=proto.success)
