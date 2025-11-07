"""Database factory module for creating database connections."""

from typing import Optional

from src.core.config import settings
from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection


class DatabaseFactory:
    """Factory for creating database connections with proper configuration."""

    @staticmethod
    def create_redis_connection(
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
    ) -> RedisConnection:
        """Create a Redis connection with optional custom configuration."""
        return RedisConnection(
            host=host or settings.REDIS_HOST,
            port=port or settings.REDIS_PORT,
            db=db or settings.REDIS_DB,
            password=password or settings.REDIS_PASSWORD,
        )

    @staticmethod
    def create_mongo_connection(
        uri: Optional[str] = None,
        database: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> MongoConnection:
        """Create a MongoDB connection with optional custom configuration."""
        return MongoConnection(
            uri=uri or str(settings.MONGO_URI),
            database=database or settings.MONGO_DB,
            collection=collection or settings.MONGO_TASKS_COLLECTION,
        )

    @staticmethod
    def create_mongo_tasks_connection() -> MongoConnection:
        """Create MongoDB connection for tasks collection."""
        return MongoConnection(
            str(settings.MONGO_URI),
            settings.MONGO_DB,
            settings.MONGO_TASKS_COLLECTION,
        )

    @staticmethod
    def create_mongo_schemas_connection() -> MongoConnection:
        """Create MongoDB connection for schemas collection."""
        return MongoConnection(
            str(settings.MONGO_URI),
            settings.MONGO_DB,
            settings.MONGO_SCHEMAS_COLLECTION,
        )
