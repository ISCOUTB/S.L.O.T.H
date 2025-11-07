"""Redis service operations module.

This module provides high-level Redis service operations that wrap
the lower-level Redis database operations. It implements the service
layer pattern to handle Redis operations with proper request/response
data structures and error handling.

The module uses proto_utils for type definitions and provides methods
for basic Redis operations like get, set, delete, and cache management.
"""

import json

from proto_utils.database import dtypes

from src.core.database_redis import redis_db


class RedisService:
    """Redis service layer class.

    Provides high-level Redis operations with proper request/response handling.
    This class acts as a service layer between the API endpoints and the
    lower-level Redis database operations, ensuring proper data validation
    and error handling.
    """

    @staticmethod
    def get_keys(request: dtypes.RedisGetKeysRequest) -> dtypes.RedisGetKeysResponse:
        """Retrieve keys matching the given pattern from Redis.

        Args:
            request (dtypes.RedisGetKeysRequest): Request containing the pattern
                to match keys against.

        Returns:
            dtypes.RedisGetKeysResponse: Response containing the list of matching keys.
        """
        keys = redis_db.keys(pattern=request["pattern"])
        return dtypes.RedisGetKeysResponse(keys=keys)

    @staticmethod
    def set_value(request: dtypes.RedisSetRequest) -> dtypes.RedisSetResponse:
        """Set a key-value pair in Redis cache.

        Args:
            request (dtypes.RedisSetRequest): Request containing the key, value,
                and optional expiration time.

        Returns:
            dtypes.RedisSetResponse: Response indicating success or failure.
        """
        try:
            redis_db.set(
                key=request["key"],
                value=request["value"],
                ex_secs=request["expiration"],
            )
            return dtypes.RedisSetResponse(success=True)
        except Exception:
            return dtypes.RedisSetResponse(success=False)

    @staticmethod
    def get_value(request: dtypes.RedisGetRequest) -> dtypes.RedisGetResponse:
        """Retrieve a value from the Redis cache by key.

        Args:
            request (dtypes.RedisGetRequest): Request containing the key to retrieve.

        Returns:
            dtypes.RedisGetResponse: Response containing the value and found status.
        """
        value = redis_db.get(key=request["key"])
        return dtypes.RedisGetResponse(value=value, found=value is not None)

    @staticmethod
    def delete_key(request: dtypes.RedisDeleteRequest) -> dtypes.RedisDeleteResponse:
        """Delete one or more keys from the Redis cache.

        Args:
            request (dtypes.RedisDeleteRequest): Request containing the keys to delete.

        Returns:
            dtypes.RedisDeleteResponse: Response containing the count of deleted keys.
        """
        deleted_count = redis_db.delete(*request["keys"])
        return dtypes.RedisDeleteResponse(count=deleted_count)

    @staticmethod
    def ping(_: dtypes.RedisPingRequest = None) -> dtypes.RedisPingResponse:
        """Check if the Redis server is reachable.

        Args:
            _ (dtypes.RedisPingRequest, optional): Unused ping request parameter.

        Returns:
            dtypes.RedisPingResponse: Response indicating if Redis is alive.
        """
        pong = redis_db.ping()
        return dtypes.RedisPingResponse(pong=pong)

    @staticmethod
    def get_cache(
        _: dtypes.RedisGetCacheRequest = None,
    ) -> dtypes.RedisGetCacheResponse:
        """Retrieve all keys and their values from the Redis cache.

        Warning: This operation can be expensive on large datasets.

        Args:
            _ (dtypes.RedisGetCacheRequest): Unused cache request parameter.

        Returns:
            dtypes.RedisGetCacheResponse: Response containing all cache data.
        """
        cache_data = redis_db.get_cache()
        return dtypes.RedisGetCacheResponse(
            cache=dict(map(lambda x: (x[0], json.dumps(x[1])), cache_data.items()))
        )

    @staticmethod
    def clear_cache(
        _: dtypes.RedisClearCacheRequest = None,
    ) -> dtypes.RedisClearCacheResponse:
        """Clear all keys and values from the Redis database.

        Warning: This operation will permanently delete all data in the
        current Redis database. Use with caution.

        Args:
            _ (dtypes.RedisClearCacheRequest): Unused clear cache request parameter.

        Returns:
            dtypes.RedisClearCacheResponse: Response indicating success or failure.
        """
        cleared = redis_db.clear_cache()
        return dtypes.RedisClearCacheResponse(success=cleared)
