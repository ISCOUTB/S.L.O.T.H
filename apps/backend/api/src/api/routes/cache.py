import json

from fastapi import APIRouter
from src.core.database_client import database_client
from proto_utils.database import dtypes

router = APIRouter()


@router.get("")
async def get_cache() -> dict:
    """
    Get all cached data from Redis.
    This endpoint retrieves all keys and their values from the Redis cache.
    """
    response = database_client.redis_get_cache()
    return dict(map(lambda x: (x[0], json.loads(x[1])), response["cache"].items()))


@router.delete("/clear")
async def clear_cache() -> dtypes.RedisClearCacheResponse:
    """
    Clear the Redis cache.
    This endpoint clears all cached data in Redis.
    """
    return database_client.clear_cache()
