import json

from fastapi import APIRouter, Depends
from proto_utils.database import DatabaseClient, dtypes

from src.api.deps import get_db_client

router = APIRouter()


@router.get("")
async def get_cache(database_client: DatabaseClient = Depends(get_db_client)) -> dict:
    """
    Get all cached data from Redis.
    This endpoint retrieves all keys and their values from the Redis cache.
    """
    response = database_client.redis_get_cache()
    return dict(map(lambda x: (x[0], json.loads(x[1])), response["cache"].items()))


@router.delete("/clear")
async def clear_cache(
    database_client: DatabaseClient = Depends(get_db_client),
) -> dtypes.RedisClearCacheResponse:
    """
    Clear the Redis cache.
    This endpoint clears all cached data in Redis.
    """
    return database_client.clear_cache()
