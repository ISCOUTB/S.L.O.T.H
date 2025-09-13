from typing import Dict, Any, List, Optional

from proto_utils.database import dtypes
from src.core.database_redis import redis_db
from src.core.database_mongo import mongo_tasks_connection


class DatabaseTasksService:
    @staticmethod
    def update_task_id(
        request: dtypes.UpdateTaskIdRequest,
    ) -> dtypes.UpdateTaskIdResponse:
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
    def set_task_id(request: dtypes.SetTaskIdRequest) -> dtypes.SetTaskIdResponse:
        try:
            # Set task in redis
            redis_db.set_task_id(
                task_id=request["task_id"], value=request["value"].copy(), task=request["task"]
            )

            # Set task in Mongo
            _set_task_id_mongo(
                task_id=request["task_id"], value=request["value"].copy(), task=request["task"]
            )

            return dtypes.SetTaskIdResponse(
                success=True, message="Task set successfully in both Redis and MongoDB"
            )
        except Exception as e:
            return dtypes.SetTaskIdResponse(
                success=False, message=f"Error setting task: {str(e)}"
            )

    @staticmethod
    def get_task_id(request: dtypes.GetTaskIdRequest) -> dtypes.GetTaskIdResponse:
        try:
            # Try to get from Redis first (faster)
            redis_result = redis_db.get_task_id(request["task_id"], request["task"])
            if redis_result:
                return dtypes.GetTaskIdResponse(value=redis_result, found=True)

            # Fallback to MongoDB
            mongo_result = _get_task_id_mongo(request["task_id"], request["task"])
            if mongo_result:
                return dtypes.GetTaskIdResponse(value=mongo_result, found=True)

            return dtypes.GetTaskIdResponse(value=None, found=False)
        except Exception:
            return dtypes.GetTaskIdResponse(value=None, found=False)

    @staticmethod
    def get_tasks_by_import_name(
        request: dtypes.GetTasksByImportNameRequest,
    ) -> dtypes.GetTasksByImportNameResponse:
        try:
            # Try Redis first
            redis_tasks = redis_db.get_tasks_by_import_name(
                request["import_name"], request["task"]
            )
            if redis_tasks:
                return dtypes.GetTasksByImportNameResponse(tasks=redis_tasks)

            # Fallback to MongoDB
            mongo_tasks = _get_tasks_by_import_name_mongo(
                request["import_name"], request["task"]
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
) -> None:
    """Update a specific field in a task ID's data in MongoDB.

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


def _set_task_id_mongo(task_id: str, value: dtypes.ApiResponse, task: str) -> None:
    """Set a task ID with associated data in MongoDB.

    Args:
        task_id (str): Unique identifier for the task.
        value (dtypes.ApiResponse): ApiResponse object containing task data.
        task (str): The task or context under which the task is being stored.

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


def _get_task_id_mongo(task_id: str, task: str) -> Optional[dtypes.ApiResponse]:
    """Retrieve a task by its ID from MongoDB.

    Args:
        task_id (str): Unique identifier for the task.
        task (str): The task or context under which the task is stored.

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
    import_name: str, task: str
) -> List[dtypes.ApiResponse]:
    """Retrieve all tasks associated with a specific import name from MongoDB.

    Args:
        import_name (str): The import name to filter tasks by.
        task (str): The task or context under which the tasks are stored.

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
