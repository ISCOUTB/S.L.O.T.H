from services.redis import RedisService
from proto_utils.generated.database import redis_pb2
from proto_utils.database.redis_serde import RedisSerde


class RedisHandler:
    @staticmethod
    def get_keys(
        request: redis_pb2.RedisGetKeysRequest,
    ) -> redis_pb2.RedisGetKeysResponse:
        deserialized_request = RedisSerde.deserialize_get_keys_request(request)
        service_response = RedisService.get_keys(deserialized_request)
        return RedisSerde.serialize_get_keys_response(service_response)

    @staticmethod
    def set(request: redis_pb2.RedisSetRequest) -> redis_pb2.RedisSetResponse:
        deserialized_request = RedisSerde.deserialize_set_request(request)
        service_response = RedisService.set_value(deserialized_request)
        return RedisSerde.serialize_set_response(service_response)

    @staticmethod
    def get(request: redis_pb2.RedisGetRequest) -> redis_pb2.RedisGetResponse:
        deserialized_request = RedisSerde.deserialize_get_request(request)
        service_response = RedisService.get_value(deserialized_request)
        return RedisSerde.serialize_get_response(service_response)

    @staticmethod
    def delete(
        request: redis_pb2.RedisDeleteRequest,
    ) -> redis_pb2.RedisDeleteResponse:
        deserialized_request = RedisSerde.deserialize_delete_request(request)
        service_response = RedisService.delete_key(deserialized_request)
        return RedisSerde.serialize_delete_response(service_response)

    @staticmethod
    def ping(
        request: redis_pb2.RedisPingRequest,
    ) -> redis_pb2.RedisPingResponse:
        deserialized_request = RedisSerde.deserialize_ping_request(request)
        service_response = RedisService.ping(deserialized_request)
        return RedisSerde.serialize_ping_response(service_response)

    @staticmethod
    def get_cache(
        request: redis_pb2.RedisGetCacheRequest,
    ) -> redis_pb2.RedisGetCacheResponse:
        deserialized_request = RedisSerde.deserialize_get_cache_request(request)
        service_response = RedisService.get_cache(deserialized_request)
        return RedisSerde.serialize_get_cache_response(service_response)

    @staticmethod
    def clear_cache(
        request: redis_pb2.RedisClearCacheRequest,
    ) -> redis_pb2.RedisClearCacheResponse:
        deserialized_request = RedisSerde.deserialize_clear_cache_request(request)
        service_response = RedisService.clear_cache(deserialized_request)
        return RedisSerde.serialize_clear_cache_response(service_response)
