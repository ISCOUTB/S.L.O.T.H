"""Redis database operations module.

This module provides Redis client operations for caching and data management.
It includes general-purpose Redis operations and specialized functions for
managing task IDs and import-related data structures.

The module uses Redis hash sets and sets for efficient storage and retrieval
of task data and maintains relationships between import names and their
associated tasks.
"""

import json
from typing import Any

from redis import Redis
import redis.exceptions
from src.core.config import settings
from src.schemas.messaging import ApiResponse


class RedisConnection:
    def __init__(
        self, host: str, port: int, db: int, password: str | None = None
    ) -> None:
        self.__host = host
        self.__port = port
        self.__db = db
        self.__password = password

        try:
            self.redis_client = Redis(
                host=self.__host,
                port=self.__port,
                db=self.__db,
                password=self.__password,
                decode_responses=True,
            )
        except redis.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Could not connect to Redis at {self.__host}:{self.__port} - {str(e)}"
            )

    @property
    def host(self) -> str:
        """Get the Redis host."""
        return self.__host

    @property
    def port(self) -> int:
        """Get the Redis port."""
        return self.__port

    @property
    def db(self) -> int:
        """Get the Redis database number."""
        return self.__db

    @property
    def password(self) -> str | None:
        """Get the Redis password."""
        return self.__password

    # @property
    # def redis_client(self) -> Redis:
    #     """Get the Redis client instance."""
    #     return self.redis_client

    # =================== General Purpose ===================

    def keys(self, pattern: str) -> list[str]:
        """Retrieve keys matching the given patterns from Redis.

        Args:
            pattern: Variable number of patterns to match keys.

        Returns:
            List of keys matching the specified patterns.
        """
        return self.redis_client.keys(pattern)

    def set(self, key: str, value: str, ex_secs: int | None = None) -> None:
        """Set a key-value pair in Redis cache.

        Args:
            key (str): The Redis key to set.
            value (str): The value to store.
            ex_secs (int): Optional expiration time in seconds.

        Returns:
            None
        """
        self.redis_client.set(key, value, ex=ex_secs)

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the Redis cache by key.

        Args:
            key: The Redis key to retrieve.

        Returns:
            The value associated with the key, or None if key doesn't exist.
        """
        return self.redis_client.get(key)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from the Redis cache.

        Args:
            *keys: Variable number of Redis keys to delete.

        Returns:
            The number of keys that were successfully deleted.
        """
        return self.redis_client.delete(*keys)

    def ping(self) -> bool:
        """Check if the Redis server is reachable.

        Returns:
            True if the server is reachable, False otherwise.
        """
        return self.redis_client.ping()

    # ================= Related to tasks_ids =================

    def update_task_id(
        self,
        task_id: str,
        field: str,
        value: Any,
        endpoint: str,
        *,
        message: str = "",
        data: dict | None = None,
        reset_data: bool = False,
    ) -> None:
        """Update a specific field in a task ID's data in the Redis cache.

        Args:
            task_id: Unique identifier for the task.
            field: The field to update in the task data.
            value: The new value to set for the specified field.
            endpoint: The endpoint or context under which the task is stored.
            message: Optional message to log or store with the update.
            data: Optional additional data to merge with existing task data.
            reset_data: If True, reset the existing data before merging new data.

        Returns:
            None
        """
        task_key = f"{endpoint}:task:{task_id}"
        if isinstance(value, dict):
            value = json.dumps(value)
        self.redis_client.hset(task_key, field, value)

        if message:
            self.redis_client.hset(task_key, "message", message)

        if data:
            cached_data = (
                self.get_task_id(task_id, endpoint).data if not reset_data else {}
            )
            cached_data = {**cached_data, **data}
            self.redis_client.hset(task_key, "data", json.dumps(cached_data))

    def set_task_id(self, task_id: str, value: ApiResponse, endpoint: str) -> None:
        """Set a task ID with associated data in the Redis cache.

        Stores the task data as a hash and adds the task ID to the import name's
        task set for efficient querying by import name.

        Args:
            task_id: Unique identifier for the task.
            value: ApiResponse object containing task data.
            endpoint: The endpoint or context under which the task is being stored.

        Returns:
            None
        """
        import_name = value.data.get("import_name", "default")
        value = value.model_dump()
        value["data"] = json.dumps(value["data"])

        task_key = f"{endpoint}:task:{task_id}"
        import_key = f"{endpoint}:import:{import_name}:tasks"
        self.redis_client.hmset(task_key, value)
        self.redis_client.sadd(import_key, task_id)

    def get_task_id(self, task_id: str, endpoint: str) -> ApiResponse | None:
        """Retrieve a task by its ID from the Redis cache.

        Args:
            task_id: Unique identifier for the task.
            endpoint: The endpoint or context under which the task is stored.

        Returns:
            ApiResponse object if task exists, None otherwise.
        """
        task_data = self.redis_client.hgetall(f"{endpoint}:task:{task_id}")
        task_data["data"] = json.loads(task_data["data"]) if "data" in task_data else {}
        try:
            return ApiResponse(**task_data)
        except Exception:
            return None

    def get_tasks_by_import_name(
        self, import_name: str, endpoint: str
    ) -> list[ApiResponse]:
        """Retrieve all tasks associated with a specific import name.

        Args:
            import_name: The import name to filter tasks by.
            endpoint: The endpoint or context under which the tasks are stored.

        Returns:
            List of ApiResponse objects for all tasks with the given import name.
            Returns empty list if no tasks found.
        """
        task_ids = self.redis_client.smembers(f"{endpoint}:import:{import_name}:tasks")
        tasks = []
        for task_id in task_ids:
            task_data = self.redis_client.hgetall(f"{endpoint}:task:{task_id}")
            if not task_data:
                continue
            task_data["data"] = (
                json.loads(task_data["data"]) if "data" in task_data else {}
            )
            tasks.append(ApiResponse(**task_data))
        return tasks

    # =================== Manage all cache ===================

    def get_cache(self) -> dict[str, Any]:
        """Retrieve all keys and their values from the Redis cache.

        Warning: This operation can be expensive on large datasets as it
        retrieves all keys and values from the Redis instance.

        Returns:
            Dictionary mapping all Redis keys to their corresponding values.
        """
        keys = self.redis_client.keys("*")
        cache_data = {}

        for key in keys:
            key_type = self.redis_client.type(key)

            if key_type == "string":
                value = self.redis_client.get(key)
                try:
                    cache_data[key] = json.loads(value) if value else None
                except (json.JSONDecodeError, TypeError):
                    cache_data[key] = value
            elif key_type == "hash":
                cache_data[key] = self.redis_client.hgetall(key)
                if "data" in cache_data[key]:
                    try:
                        cache_data[key]["data"] = json.loads(cache_data[key]["data"])
                    except (json.JSONDecodeError, TypeError):
                        pass
            elif key_type == "set":
                cache_data[key] = list(self.redis_client.smembers(key))
            elif key_type == "list":
                cache_data[key] = self.redis_client.lrange(key, 0, -1)
            elif key_type == "zset":
                cache_data[key] = self.redis_client.zrange(key, 0, -1, withscores=True)
            else:
                cache_data[key] = f"Unsupported type: {key_type}"

        return cache_data

    def clear_cache(self) -> bool:
        """Clear all keys and values from the Redis database.

        Warning: This operation will permanently delete all data in the
        current Redis database. Use with caution.

        Returns:
            Redis response confirming the flush operation.
        """
        try:
            return self.redis_client.flushdb()
        except redis.exceptions.ConnectionError:
            return False


redis_db = RedisConnection(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
)
