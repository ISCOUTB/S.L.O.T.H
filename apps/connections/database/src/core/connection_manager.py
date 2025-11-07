from contextlib import contextmanager
from typing import Generator, Optional

import pymongo.errors
import redis.exceptions

from src.core.database_factory import DatabaseFactory
from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection
from src.utils.logger import logger


class ConnectionManager:
    def __init__(self):
        self._redis_connection: Optional[RedisConnection] = None
        self._mongo_tasks_connection: Optional[MongoConnection] = None
        self._mongo_schemas_connection: Optional[MongoConnection] = None

    def get_redis_connection(self, force_reconnect: bool = False) -> RedisConnection:
        """Get Redis connection with automatic reconnection on failure.

        Args:
            force_reconnect: Force creation of a new connection.

        Returns:
            RedisConnection: Active Redis connection.
        """
        # Force reconnect or connection doesn't exist
        if force_reconnect or self._redis_connection is None:
            logger.info("Creating new Redis connection")
            self._redis_connection = DatabaseFactory.create_redis_connection()
            return self._redis_connection

        # Check if existing connection is healthy
        if not self._redis_connection.is_healthy():
            logger.warning("Redis connection unhealthy, reconnecting...")
            try:
                # Close old connection
                if self._redis_connection:
                    self._redis_connection.redis_client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

            # Create new connection
            self._redis_connection = DatabaseFactory.create_redis_connection()
            logger.info("Redis reconnection successful")

        return self._redis_connection

    def get_mongo_tasks_connection(
        self, force_reconnect: bool = False
    ) -> MongoConnection:
        """Get MongoDB tasks connection with automatic reconnection on failure.

        Args:
            force_reconnect: Force creation of a new connection.

        Returns:
            MongoConnection: Active MongoDB connection.
        """
        if force_reconnect or self._mongo_tasks_connection is None:
            logger.info("Creating new MongoDB tasks connection")
            self._mongo_tasks_connection = (
                DatabaseFactory.create_mongo_tasks_connection()
            )
            return self._mongo_tasks_connection

        if not self._mongo_tasks_connection.is_healthy():
            logger.warning("MongoDB tasks connection unhealthy, reconnecting...")
            try:
                if self._mongo_tasks_connection:
                    self._mongo_tasks_connection.client.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB tasks connection: {e}")

            self._mongo_tasks_connection = (
                DatabaseFactory.create_mongo_tasks_connection()
            )
            logger.info("MongoDB tasks reconnection successful")

        return self._mongo_tasks_connection

    def get_mongo_schemas_connection(
        self, force_reconnect: bool = False
    ) -> MongoConnection:
        """Get MongoDB schemas connection with automatic reconnection on failure.

        Args:
            force_reconnect: Force creation of a new connection.

        Returns:
            MongoConnection: Active MongoDB connection.
        """
        if force_reconnect or self._mongo_schemas_connection is None:
            logger.info("Creating new MongoDB schemas connection")
            self._mongo_schemas_connection = (
                DatabaseFactory.create_mongo_schemas_connection()
            )
            return self._mongo_schemas_connection

        if not self._mongo_schemas_connection.is_healthy():
            logger.warning("MongoDB schemas connection unhealthy, reconnecting...")
            try:
                if self._mongo_schemas_connection:
                    self._mongo_schemas_connection.client.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB schemas connection: {e}")

            self._mongo_schemas_connection = (
                DatabaseFactory.create_mongo_schemas_connection()
            )
            logger.info("MongoDB schemas reconnection successful")

        return self._mongo_schemas_connection

    @contextmanager
    def redis_connection(self) -> Generator[RedisConnection, None, None]:
        """Context manager for Redis connection with automatic health check.

        Yields:
            RedisConnection: Active Redis connection.

        Example:
            >>> with manager.redis_connection() as redis:
            ...     redis.set("key", "value")
        """
        conn = self.get_redis_connection()
        try:
            yield conn
        except (
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
            redis.exceptions.ResponseError,
        ) as e:
            logger.error(f"Redis operation failed: {e}, attempting reconnection")
            raise

    @contextmanager
    def mongo_tasks_connection(self) -> Generator[MongoConnection, None, None]:
        """Context manager for MongoDB tasks connection with automatic health check.

        Yields:
            MongoConnection: Active MongoDB tasks connection.

        Example:
            >>> with manager.mongo_tasks_connection() as mongo:
            ...     mongo.insert_one({"task_id": "123", "status": "pending"})
        """
        conn = self.get_mongo_tasks_connection()
        try:
            yield conn
        except (
            pymongo.errors.ConnectionFailure,
            pymongo.errors.ServerSelectionTimeoutError,
        ) as e:
            logger.error(
                f"MongoDB tasks operation failed: {e}, attempting reconnection"
            )
            raise

    @contextmanager
    def mongo_schemas_connection(self) -> Generator[MongoConnection, None, None]:
        """Context manager for MongoDB schemas connection with automatic health check.

        Yields:
            MongoConnection: Active MongoDB schemas connection.

        Example:
            >>> with manager.mongo_schemas_connection() as mongo:
            ...     mongo.insert_one({"schema_name": "users", "version": 1})
        """
        conn = self.get_mongo_schemas_connection()
        try:
            yield conn
        except (
            pymongo.errors.ConnectionFailure,
            pymongo.errors.ServerSelectionTimeoutError,
        ) as e:
            logger.error(
                f"MongoDB schemas operation failed: {e}, attempting reconnection"
            )
            raise

    def close_all(self):
        """Close all active connections gracefully."""
        logger.info("Closing all database connections")

        if self._redis_connection:
            try:
                self._redis_connection.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis: {e}")

        if self._mongo_tasks_connection:
            try:
                self._mongo_tasks_connection.client.close()
                logger.info("MongoDB tasks connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB tasks: {e}")

        if self._mongo_schemas_connection:
            try:
                self._mongo_schemas_connection.client.close()
                logger.info("MongoDB schemas connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB schemas: {e}")


_connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance.

    Returns:
        ConnectionManager: Global connection manager.
    """
    return _connection_manager


def set_connection_manager(manager: ConnectionManager) -> None:
    """Set a custom connection manager (useful for testing).

    Args:
        manager: Custom connection manager instance.
    """
    global _connection_manager
    _connection_manager = manager
