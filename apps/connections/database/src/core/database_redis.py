"""Redis database operations module.

This module provides Redis client operations for caching and data management.
It includes general-purpose Redis operations and specialized functions for
managing task IDs and import-related data structures.

The module uses Redis hash sets and sets for efficient storage and retrieval
of task data and maintains relationships between import names and their
associated tasks.
"""

import json
from typing import Any, Dict, List, Optional

import redis.exceptions
from proto_utils.database.dtypes import ApiResponse
from redis import Redis

from src.core.config import settings


class RedisConnection:
    def __init__(
        self, host: str, port: int, db: int, password: Optional[str] = None
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
    def password(self) -> Optional[str]:
        """Get the Redis password."""
        return self.__password

    # =================== General Purpose ===================

    def keys(self, pattern: str) -> List[str]:
        """Retrieve keys matching the given patterns from Redis.

        Args:
            pattern (str): Variable number of patterns to match keys.

        Returns:
            List[str]: List of keys matching the specified patterns.
        """
        return self.redis_client.keys(pattern)

    def set(self, key: str, value: str, ex_secs: Optional[int] = None) -> None:
        """Set a key-value pair in Redis cache.

        Args:
            key (str): The Redis key to set.
            value (str): The value to store.
            ex_secs (Optional[int]): Optional expiration time in seconds.

        Returns:
            None:
        """
        if ex_secs is None or ex_secs <= 0:
            ex_secs = settings.DEFAULT_TTL_SECONDS
        self.redis_client.set(key, value, ex=ex_secs)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the Redis cache by key.

        Args:
            key (str): The Redis key to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if key doesn't exist.
        """
        return self.redis_client.get(key)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from the Redis cache.

        Args:
            *keys (str): Variable number of Redis keys to delete.

        Returns:
            int: The number of keys that were successfully deleted.
        """
        return self.redis_client.delete(*keys)

    def ping(self) -> bool:
        """Check if the Redis server is reachable.

        Returns:
            bool: True if the server is reachable, False otherwise.
        """
        return self.redis_client.ping()

    def is_healthy(self) -> bool:
        """Internal method to check Redis health.

        Returns:
            bool: True if Redis is healthy, False otherwise.
        """
        try:
            return self.redis_client.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return False

    def _get_task_ttl(self, status: str) -> int:
        """
        Get TTL based on task status.

        Args:
            status (str): The current status of the task.

        Returns:
            int: TTL in seconds corresponding to the task status.
        """
        # TODO: Use Literal type hints to standardize possible status values across microservices

        ttl_mapping = {
            # Common task statuses
            "accepted": settings.TASK_TTL_PENDING_SECONDS,
            "error": settings.TASK_TTL_FAILED_SECONDS,
            "completed": settings.TASK_TTL_COMPLETED_SECONDS,
            "failed-publishing-result": settings.TASK_TTL_FAILED_SECONDS,
            "published": settings.TASK_TTL_PUBLISHED_SECONDS,
            # Validation task
            "received-sample-validation": settings.TASK_TTL_PROCESSING_SECONDS,
            "processing-file": settings.TASK_TTL_PROCESSING_SECONDS,
            "validating-file": settings.TASK_TTL_PROCESSING_SECONDS,
            "success": settings.TASK_TTL_PROCESSING_SECONDS,
            "warning": settings.TASK_TTL_PROCESSING_SECONDS,
            # Update JsonSchema task
            "received-schema-update": settings.TASK_TTL_PROCESSING_SECONDS,
            "received-removing-schema": settings.TASK_TTL_PROCESSING_SECONDS,
            "creating-schema": settings.TASK_TTL_PROCESSING_SECONDS,
            "schema-created": settings.TASK_TTL_PROCESSING_SECONDS,
            "failed-creating-schema": settings.TASK_TTL_FAILED_SECONDS,
            "saving-schema": settings.TASK_TTL_PROCESSING_SECONDS,
            "failed-saving-schema": settings.TASK_TTL_FAILED_SECONDS,
            # Remove JsonSchema task
            "removing-schema": settings.TASK_TTL_PROCESSING_SECONDS,
            "failed-removing-schema": settings.TASK_TTL_FAILED_SECONDS,
        }

        return ttl_mapping.get(status, settings.DEFAULT_TTL_SECONDS)

    # ================= Related to tasks_ids =================

    def update_task_id(
        self,
        task_id: str,
        field: str,
        value: Any,
        task: str,
        *,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        reset_data: bool = False,
    ) -> None:
        """Update a specific field in a task ID's data in the Redis cache.

        Args:
            task_id (str): Unique identifier for the task.
            field (str): The field to update in the task data.
            value (Any): The new value to set for the specified field.
            task (str): The task or context under which the task is stored.
            message (str): Optional message to log or store with the update.
            data (Optional[Dict[str, Any]]): Optional additional data to merge with existing task data.
            reset_data (bool): If True, reset the existing data before merging new data.

        Returns:
            None:
        """
        task_key = f"{task}:task:{task_id}"
        if isinstance(value, dict):
            value = json.dumps(value)
        self.redis_client.hset(task_key, field, value)

        if message:
            self.redis_client.hset(task_key, "message", message)

        if data:
            cached_data = (
                self.get_task_id(task_id, task)["data"] if not reset_data else {}
            )
            cached_data = {**cached_data, **data}
            self.redis_client.hset(task_key, "data", json.dumps(cached_data))

        if field == "status":
            ttl = self._get_task_ttl(value)
            self.redis_client.expire(task_key, ttl)

    def set_task_id(self, task_id: str, value: ApiResponse, task: str) -> None:
        """Set a task ID with associated data in the Redis cache.

        Stores the task data as a hash and adds the task ID to the import name's
        task set for efficient querying by import name.

        Args:
            task_id (str): Unique identifier for the task.
            value (ApiResponse): ApiResponse object containing task data.
            task (str): The task or context under which the task is being stored.

        Returns:
            None:
        """
        import_name = value["data"].get("import_name", "default")

        # Create a copy to avoid modifying the original dict
        redis_value = {
            "status": value["status"],
            "code": str(value["code"]),  # Convert to string for Redis
            "message": value["message"],
            "data": json.dumps(value["data"]),  # Serialize data dict
        }

        task_key = f"{task}:task:{task_id}"
        import_key = f"{task}:import:{import_name}:tasks"
        self.redis_client.hset(task_key, mapping=redis_value)
        self.redis_client.sadd(import_key, task_id)

        ttl = self._get_task_ttl(value["status"])
        self.redis_client.expire(task_key, ttl)
        self.redis_client.expire(import_key, ttl)

    def get_task_id(self, task_id: str, task: str) -> Optional[ApiResponse]:
        """Retrieve a task by its ID from the Redis cache.

        Args:
            task_id (str): Unique identifier for the task.
            task (str): The task or context under which the task is stored.

        Returns:
            Optional[ApiResponse]: ApiResponse object if task exists, None otherwise.
        """
        task_data = self.redis_client.hgetall(f"{task}:task:{task_id}")

        if not task_data:
            return None

        # Since decode_responses=True in Redis client, data is already decoded
        # Just need to convert types
        if "data" in task_data:
            task_data["data"] = json.loads(task_data["data"])

        if "code" in task_data:
            task_data["code"] = int(task_data["code"])

        try:
            return ApiResponse(**task_data)
        except Exception:
            return None

    def get_tasks_by_import_name(
        self, import_name: str, task: str
    ) -> List[ApiResponse]:
        """Retrieve all tasks associated with a specific import name.

        Args:
            import_name (str): The import name to filter tasks by.
            task (str): The task or context under which the tasks are stored.

        Returns:
            List[ApiResponse]: List of ApiResponse objects for all tasks with the given import name.
            Returns empty list if no tasks found.
        """
        task_ids = self.redis_client.smembers(f"{task}:import:{import_name}:tasks")
        tasks = []
        for task_id in task_ids:
            task_data = self.redis_client.hgetall(f"{task}:task:{task_id}")
            if not task_data:
                continue

            # Ensure correct types
            task_data["code"] = int(task_data["code"])

            task_data["data"] = (
                json.loads(task_data["data"]) if "data" in task_data else {}
            )
            tasks.append(ApiResponse(**task_data))
        return tasks

    # =================== Manage all cache ===================

    def get_cache(self) -> Dict[str, Any]:
        """Retrieve all keys and their values from the Redis cache.

        Warning: This operation can be expensive on large datasets as it
        retrieves all keys and values from the Redis instance.

        Returns:
            Dict[str, Any]: Dictionary mapping all Redis keys to their corresponding values.
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
            bool: Redis response confirming the flush operation.
        """
        try:
            return self.redis_client.flushdb()
        except redis.exceptions.ConnectionError:
            return False
