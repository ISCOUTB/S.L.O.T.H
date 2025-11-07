import time

from proto_utils.database import dtypes

from src.services.redis import RedisService


def test_get_keys() -> None:
    pattern = "*"
    keys = RedisService.get_keys(dtypes.RedisGetKeysRequest(pattern=pattern))
    assert isinstance(keys["keys"], list)
    assert all(isinstance(key, str) for key in keys["keys"])


def test_set_value_without_expiration() -> None:
    key = "test:example-key"
    value = "example-value"
    response = RedisService.set_value(
        dtypes.RedisSetRequest(key=key, value=value, expiration=None)
    )

    assert response["success"] is True

    get_response = RedisService.get_value(dtypes.RedisGetRequest(key=key))
    assert get_response["found"] is True
    assert get_response["value"] == value


def test_set_value_with_expiration() -> None:
    key = "test:example-key-exp"
    value = "example-value-exp"
    expiration_secs = 2
    response = RedisService.set_value(
        dtypes.RedisSetRequest(key=key, value=value, expiration=expiration_secs)
    )

    assert response["success"] is True

    # Wait for the key to expire
    time.sleep(expiration_secs + 0.5)

    get_response = RedisService.get_value(dtypes.RedisGetRequest(key=key))
    assert get_response["found"] is False
    assert get_response["value"] is None


def test_get_value_existing_key() -> None:
    key = "test:existing-key"
    value = "existing-value"
    RedisService.set_value(
        dtypes.RedisSetRequest(key=key, value=value, expiration=None)
    )

    get_response = RedisService.get_value(dtypes.RedisGetRequest(key=key))

    assert get_response["found"] is True
    assert get_response["value"] == value


def test_get_value_non_existing_key() -> None:
    key = "test:non-existing-key"
    get_response = RedisService.get_value(dtypes.RedisGetRequest(key=key))

    assert get_response["found"] is False
    assert get_response["value"] is None


def test_delete_existing_keys() -> None:
    key1 = "test:delete-key1"
    key2 = "test:delete-key2"
    RedisService.set_value(
        dtypes.RedisSetRequest(key=key1, value="value1", expiration=None)
    )
    RedisService.set_value(
        dtypes.RedisSetRequest(key=key2, value="value2", expiration=None)
    )

    delete_response = RedisService.delete_key(
        dtypes.RedisDeleteRequest(keys=[key1, key2])
    )

    assert delete_response["count"] == 2

    get_response1 = RedisService.get_value(dtypes.RedisGetRequest(key=key1))
    get_response2 = RedisService.get_value(dtypes.RedisGetRequest(key=key2))

    assert get_response1["found"] is False
    assert get_response2["found"] is False


def test_delete_non_existing_keys() -> None:
    key1 = "test:non-existing-delete-key1"
    key2 = "test:non-existing-delete-key2"

    delete_response = RedisService.delete_key(
        dtypes.RedisDeleteRequest(keys=[key1, key2])
    )

    assert delete_response["count"] == 0


def test_ping() -> None:
    ping_response = RedisService.ping()
    assert ping_response["pong"] is True


def test_get_cache() -> None:
    cache_response = RedisService.get_cache(dtypes.RedisGetCacheRequest())
    assert isinstance(cache_response["cache"], dict)


def test_clear_cache() -> None:
    clear_response = RedisService.clear_cache(dtypes.RedisClearCacheRequest())
    assert clear_response["success"] is True

    # Verify cache is cleared
    cache_response = RedisService.get_cache(dtypes.RedisGetCacheRequest())
    assert isinstance(cache_response["cache"], dict)
    assert len(cache_response["cache"]) == 0
