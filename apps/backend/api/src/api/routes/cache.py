from fastapi import APIRouter
from src.core.database_redis import redis_db

router = APIRouter()


@router.get("")
async def get_cache() -> dict:
    """
    Get all cached data from Redis.
    This endpoint retrieves all keys and their values from the Redis cache.
    """
    return redis_db.get_cache()


@router.delete("/clear")
async def clear_cache() -> bool:
    """
    Clear the Redis cache.
    This endpoint clears all cached data in Redis.
    """
    return redis_db.clear_cache()
