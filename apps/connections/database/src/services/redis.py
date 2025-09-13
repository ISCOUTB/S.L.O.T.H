from proto_utils.database import dtypes
from src.core.database_redis import redis_db


class RedisService:
    @staticmethod
    def get_keys(request: dtypes.RedisGetKeysRequest) -> dtypes.RedisGetKeysResponse:
        keys = redis_db.keys(pattern=request["pattern"])
        return dtypes.RedisGetKeysResponse(keys=keys)

    @staticmethod
    def set_value(request: dtypes.RedisSetRequest) -> dtypes.RedisSetResponse:
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
        value = redis_db.get(key=request["key"])
        return dtypes.RedisGetResponse(value=value, found=value is not None)

    @staticmethod
    def delete_key(request: dtypes.RedisDeleteRequest) -> dtypes.RedisDeleteResponse:
        deleted_count = redis_db.delete(*request["keys"])
        return dtypes.RedisDeleteResponse(count=deleted_count)

    @staticmethod
    def ping(_: dtypes.RedisPingRequest = None) -> dtypes.RedisPingResponse:
        is_alive = redis_db.ping()
        return dtypes.RedisPingResponse(alive=is_alive)

    @staticmethod
    def get_cache(_: dtypes.RedisGetCacheRequest) -> dtypes.RedisGetCacheResponse:
        cache_data = redis_db.get_cache()
        return dtypes.RedisGetCacheResponse(cache=cache_data)

    @staticmethod
    def clear_cache(_: dtypes.RedisClearCacheRequest) -> dtypes.RedisClearCacheResponse:
        cleared = redis_db.clear_cache()
        return dtypes.RedisClearCacheResponse(success=cleared)
