"""Database tasks service operations module.

This module provides high-level database operations for task management
across both Redis and MongoDB. It implements a dual-storage strategy
where Redis serves as a fast cache and MongoDB provides persistent storage
with automatic synchronization between both databases.

The module includes task CRUD operations with built-in fallback mechanisms
and data consistency management between the two storage systems.
"""

from typing import Any, Dict, List, Optional

from proto_utils.database import dtypes

from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection


class DatabaseTasksService:
    """Database tasks service layer class.

    Provides high-level task management operations with dual-storage strategy.
    This class manages tasks in both Redis (for fast access) and MongoDB
    (for persistence), ensuring data consistency and providing fallback
    mechanisms when one storage system is unavailable.
    """

    @staticmethod
    def update_task_id(
        request: dtypes.UpdateTaskIdRequest,
        *,
        redis_db: RedisConnection,
        mongo_tasks_connection: MongoConnection,
    ) -> dtypes.UpdateTaskIdResponse:
        """Update a specific field in a task across both Redis and MongoDB.

        This method updates task information in both storage systems to maintain
        consistency. Updates are performed in Redis first for speed, then in
        MongoDB for persistence.

        Args:
            request (dtypes.UpdateTaskIdRequest): Request containing task ID,
                field to update, new value, and optional message and data.
            redis_db (RedisConnection): Active Redis connection.
            mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

        Returns:
            dtypes.UpdateTaskIdResponse: Response indicating success or failure
                of the update operation.
        """
        try:
            # Update task in redis
            redis_db.update_task_id(
                task_id=request["task_id"],
                field=request["field"],
                value=request["value"],
                task=request["task"],
                message=request.get("message", ""),
                data=request.get("data", None),
                reset_data=request.get("reset_data", False),
            )

            # Update task in Mongo
            _update_task_id_mongo(
                task_id=request["task_id"],
                field=request["field"],
                value=request["value"],
                task=request["task"],
                message=request.get("message", ""),
                data=request.get("data", None),
                reset_data=request.get("reset_data", False),
                mongo_tasks_connection=mongo_tasks_connection,
            )

            return dtypes.UpdateTaskIdResponse(
                success=True,
                message="Task updated successfully in both Redis and MongoDB",
            )
        except Exception as e:
            return dtypes.UpdateTaskIdResponse(
                success=False, message=f"Error updating task: {str(e)}"
            )

    @staticmethod
    def set_task_id(
        request: dtypes.SetTaskIdRequest,
        *,
        redis_db: RedisConnection,
        mongo_tasks_connection: MongoConnection,
    ) -> dtypes.SetTaskIdResponse:
        """Create or replace a task in both Redis and MongoDB.

        This method sets task data in both storage systems simultaneously
        to ensure consistency and availability.

        Args:
            request (dtypes.SetTaskIdRequest): Request containing task ID,
                task data, and context information.
            redis_db (RedisConnection): Active Redis connection.
            mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

        Returns:
            dtypes.SetTaskIdResponse: Response indicating success or failure
                of the set operation.
        """
        try:
            # Set task in redis
            redis_db.set_task_id(
                task_id=request["task_id"],
                value=request["value"].copy(),
                task=request["task"],
            )

            # Set task in Mongo
            _set_task_id_mongo(
                task_id=request["task_id"],
                value=request["value"].copy(),
                task=request["task"],
                mongo_tasks_connection=mongo_tasks_connection,
            )

            return dtypes.SetTaskIdResponse(
                success=True, message="Task set successfully in both Redis and MongoDB"
            )
        except Exception as e:
            return dtypes.SetTaskIdResponse(
                success=False, message=f"Error setting task: {str(e)}"
            )

    @staticmethod
    def get_task_id(
        request: dtypes.GetTaskIdRequest,
        redis_db: RedisConnection,
        mongo_tasks_connection: MongoConnection,
    ) -> dtypes.GetTaskIdResponse:
        """Retrieve a task by ID with fallback mechanism.

        This method attempts to retrieve the task from Redis first (for speed),
        and falls back to MongoDB if not found. Found MongoDB results are
        automatically cached in Redis for future queries.

        Args:
            request (dtypes.GetTaskIdRequest): Request containing task ID and context.
            redis_db (RedisConnection): Active Redis connection.
            mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

        Returns:
            dtypes.GetTaskIdResponse: Response containing the task data or indicating
                if the task was not found.
        """
        try:
            # Try to get from Redis first (faster)
            redis_result = redis_db.get_task_id(request["task_id"], request["task"])
            if redis_result:
                return dtypes.GetTaskIdResponse(value=redis_result, found=True)

            # Fallback to MongoDB
            mongo_result = _get_task_id_mongo(
                request["task_id"], request["task"], mongo_tasks_connection
            )
            if mongo_result:
                # Cache the result in Redis for future queries
                redis_db.set_task_id(
                    task_id=request["task_id"],
                    value=mongo_result.copy(),
                    task=request["task"],
                )
                return dtypes.GetTaskIdResponse(value=mongo_result, found=True)

            return dtypes.GetTaskIdResponse(value=None, found=False)
        except Exception:
            return dtypes.GetTaskIdResponse(value=None, found=False)

    @staticmethod
    def get_tasks_by_import_name(
        request: dtypes.GetTasksByImportNameRequest,
        redis_db: RedisConnection,
        mongo_tasks_connection: MongoConnection,
    ) -> dtypes.GetTasksByImportNameResponse:
        """Retrieve all tasks associated with a specific import name.

        This method searches for tasks by import name with fallback mechanism.
        It tries Redis first, then MongoDB, and caches MongoDB results in Redis
        for future queries.

        Args:
            request (dtypes.GetTasksByImportNameRequest): Request containing
                import name and context.
            redis_db (RedisConnection): Active Redis connection.
            mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

        Returns:
            dtypes.GetTasksByImportNameResponse: Response containing the list of
                matching tasks.
        """
        try:
            # Try Redis first
            redis_tasks = redis_db.get_tasks_by_import_name(
                request["import_name"], request["task"]
            )
            if redis_tasks:
                return dtypes.GetTasksByImportNameResponse(tasks=redis_tasks)

            # Fallback to MongoDB
            mongo_tasks = _get_tasks_by_import_name_mongo(
                request["import_name"], request["task"], mongo_tasks_connection
            )

            # Cache all found tasks in Redis for future queries
            if mongo_tasks:
                for task_data in mongo_tasks:
                    # Extract task_id from the data field if available
                    task_id = task_data["data"].get("task_id")
                    if task_id:
                        redis_db.set_task_id(
                            task_id=task_id, value=task_data, task=request["task"]
                        )

            return dtypes.GetTasksByImportNameResponse(tasks=mongo_tasks)
        except Exception:
            return dtypes.GetTasksByImportNameResponse(tasks=[])


# ===================== MongoDB Helper Functions =====================


def _update_task_id_mongo(
    task_id: str,
    field: str,
    value: Any,
    task: str,
    *,
    message: str = "",
    data: Optional[Dict[str, Any]] = None,
    reset_data: bool = False,
    mongo_tasks_connection: MongoConnection,
) -> None:
    """Update a specific field in a task ID's data in MongoDB.

    This is a helper function that handles the MongoDB-specific update logic
    for task data. It supports both simple field updates and complex data
    merging operations.

    Args:
        task_id (str): Unique identifier for the task.
        field (str): The field to update in the task data.
        value (Any): The new value to set for the specified field.
        task (str): The task or context under which the task is stored.
        message (str): Optional message to log or store with the update.
        data (Optional[Dict[str, Any]]): Optional additional data to merge with existing task data.
        reset_data (bool): If True, reset the existing data before merging new data.
        mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

    Returns:
        None:
    """
    filter_query = {"task_id": task_id, "task": task}

    # Prepare update operations
    update_ops = {"$set": {field: value}}

    if message:
        update_ops["$set"]["message"] = message

    if data:
        if reset_data:
            update_ops["$set"]["data"] = data
        else:
            # Get existing task to merge data
            existing_task = mongo_tasks_connection.find_one(filter_query)
            existing_data = existing_task.get("data", {}) if existing_task else {}
            merged_data = {**existing_data, **data}
            update_ops["$set"]["data"] = merged_data

    mongo_tasks_connection.update_one(filter_query, update_ops)


def _set_task_id_mongo(
    task_id: str,
    value: dtypes.ApiResponse,
    task: str,
    mongo_tasks_connection: MongoConnection,
) -> None:
    """Set a task ID with associated data in MongoDB.

    This is a helper function that handles the MongoDB-specific insertion/update
    logic for task data. It uses upsert operation to either insert new tasks
    or update existing ones.

    Args:
        task_id (str): Unique identifier for the task.
        value (dtypes.ApiResponse): ApiResponse object containing task data.
        task (str): The task or context under which the task is being stored.
        mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

    Returns:
        None:
    """
    import_name = value["data"].get("import_name", "default")

    # Prepare document for MongoDB
    document = {
        "task_id": task_id,
        "task": task,
        "import_name": import_name,
        "status": value["status"],
        "code": value["code"],
        "message": value["message"],
        "data": value["data"],
    }

    # Use upsert to either insert or update
    filter_query = {"task_id": task_id, "task": task}
    mongo_tasks_connection.collection.replace_one(filter_query, document, upsert=True)


def _get_task_id_mongo(
    task_id: str,
    task: str,
    mongo_tasks_connection: MongoConnection,
) -> Optional[dtypes.ApiResponse]:
    """Retrieve a task by its ID from MongoDB.

    This is a helper function that handles the MongoDB-specific retrieval
    logic for task data. It includes proper error handling and data validation.

    Args:
        task_id (str): Unique identifier for the task.
        task (str): The task or context under which the task is stored.
        mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

    Returns:
        Optional[dtypes.ApiResponse]: ApiResponse object if task exists, None otherwise.
    """
    filter_query = {"task_id": task_id, "task": task}
    task_data = mongo_tasks_connection.find_one(filter_query)

    if not task_data:
        return None

    try:
        return dtypes.ApiResponse(
            status=task_data["status"],
            code=int(task_data["code"]),
            message=task_data["message"],
            data=task_data["data"],
        )
    except KeyError:
        return None


def _get_tasks_by_import_name_mongo(
    import_name: str,
    task: str,
    mongo_tasks_connection: MongoConnection,
) -> List[dtypes.ApiResponse]:
    """Retrieve all tasks associated with a specific import name from MongoDB.

    This is a helper function that handles the MongoDB-specific query logic
    for retrieving multiple tasks by import name. It includes proper error
    handling for malformed documents.

    Args:
        import_name (str): The import name to filter tasks by.
        task (str): The task or context under which the tasks are stored.
        mongo_tasks_connection (MongoConnection): Active MongoDB tasks connection.

    Returns:
        List[dtypes.ApiResponse]: List of ApiResponse objects for all tasks with the given import name.
        Returns empty list if no tasks found.
    """
    filter_query = {"import_name": import_name, "task": task}
    tasks_cursor = mongo_tasks_connection.collection.find(filter_query)

    tasks = []
    for task_data in tasks_cursor:
        try:
            api_response = dtypes.ApiResponse(
                status=task_data["status"],
                code=task_data["code"],
                message=task_data["message"],
                data=task_data["data"],
            )
            tasks.append(api_response)
        except KeyError:
            continue  # Skip malformed documents

    return tasks
