import time
from typing import Callable

import redis.exceptions
from proto_utils.database.redis_serde import RedisSerde
from proto_utils.generated.database import redis_pb2

from src.core.database_redis import RedisConnection
from src.handlers.base import BaseHandler, Request, T
from src.services.redis import RedisService
from src.utils.logger import logger


class RedisHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _execute_with_retry(
        self,
        operation: Callable[[Request, RedisConnection], T],
        request: Request,
    ) -> T:
        current_delay = self.retry_delay_redis
        last_exception = None

        for attempt in range(1, self.max_retries_redis + 1):
            try:
                redis_db = self.manager.get_redis_connection(attempt > 1)
                return operation(request, redis_db=redis_db)
            except (
                redis.exceptions.ConnectionError,
                redis.exceptions.TimeoutError,
                redis.exceptions.ResponseError,
            ) as e:
                last_exception = e
                if attempt == self.max_retries_redis:
                    logger.error(
                        f"Redis operation '{operation.__name__}' failed after "
                        f"{self.max_retries_redis} attempts: {e}"
                    )
                    raise

                logger.warning(
                    f"Redis operation '{operation.__name__}' failed "
                    f"(attempt {attempt}/{self.max_retries_redis}): {e}. "
                    f"Retrying in {current_delay}s..."
                )
                time.sleep(current_delay)
                current_delay *= self.backoff_redis

        # just in case
        raise last_exception

    def get_keys(
        self,
        request: redis_pb2.RedisGetKeysRequest,
    ) -> redis_pb2.RedisGetKeysResponse:
        deserialized_request = RedisSerde.deserialize_get_keys_request(request)
        service_response = self._execute_with_retry(
            RedisService.get_keys, deserialized_request
        )
        return RedisSerde.serialize_get_keys_response(service_response)

    def set(self, request: redis_pb2.RedisSetRequest) -> redis_pb2.RedisSetResponse:
        deserialized_request = RedisSerde.deserialize_set_request(request)
        service_response = self._execute_with_retry(
            RedisService.set_value, deserialized_request
        )
        return RedisSerde.serialize_set_response(service_response)

    def get(self, request: redis_pb2.RedisGetRequest) -> redis_pb2.RedisGetResponse:
        deserialized_request = RedisSerde.deserialize_get_request(request)
        service_response = self._execute_with_retry(
            RedisService.get_value, deserialized_request
        )
        return RedisSerde.serialize_get_response(service_response)

    def delete(
        self,
        request: redis_pb2.RedisDeleteRequest,
    ) -> redis_pb2.RedisDeleteResponse:
        deserialized_request = RedisSerde.deserialize_delete_request(request)
        service_response = self._execute_with_retry(
            RedisService.delete_key, deserialized_request
        )
        return RedisSerde.serialize_delete_response(service_response)

    def ping(
        self,
        request: redis_pb2.RedisPingRequest,
    ) -> redis_pb2.RedisPingResponse:
        deserialized_request = RedisSerde.deserialize_ping_request(request)
        service_response = self._execute_with_retry(
            RedisService.ping, deserialized_request
        )
        return RedisSerde.serialize_ping_response(service_response)

    def get_cache(
        self,
        request: redis_pb2.RedisGetCacheRequest,
    ) -> redis_pb2.RedisGetCacheResponse:
        deserialized_request = RedisSerde.deserialize_get_cache_request(request)
        service_response = self._execute_with_retry(
            RedisService.get_cache, deserialized_request
        )
        return RedisSerde.serialize_get_cache_response(service_response)

    def clear_cache(
        self,
        request: redis_pb2.RedisClearCacheRequest,
    ) -> redis_pb2.RedisClearCacheResponse:
        deserialized_request = RedisSerde.deserialize_clear_cache_request(request)
        service_response = self._execute_with_retry(
            RedisService.clear_cache, deserialized_request
        )
        return RedisSerde.serialize_clear_cache_response(service_response)
