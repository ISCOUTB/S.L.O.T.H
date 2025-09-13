from uuid import uuid4
from proto_utils.database import dtypes
from src.services.tasks import DatabaseTasksService

from src.core.database_redis import redis_db
from src.core.database_mongo import mongo_tasks_connection


def test_set_task_id() -> None:
    """Test setting a task ID in both Redis and MongoDB."""
    task_id = str(uuid4())
    task = "test"

    # Create a proper ApiResponse value
    api_response = dtypes.ApiResponse(
        status="success",
        code=200,
        message="Task created successfully",
        data={
            "import_name": "test_import",
            "processing_status": "pending",
            "file_name": "test.csv",
        },
    )

    # Call the method to set the task ID
    response = DatabaseTasksService.set_task_id(
        dtypes.SetTaskIdRequest(task_id=task_id, value=api_response, task=task)
    )

    # Assert the response
    assert response["success"] is True
    assert response["message"] == "Task set successfully in both Redis and MongoDB"

    # Verify that the task was set in Redis
    redis_task = redis_db.get_task_id(task_id, task)
    assert redis_task is not None
    assert redis_task["status"] == "success"
    assert redis_task["code"] == 200
    assert redis_task["data"]["import_name"] == "test_import"

    # Verify that the task was set in MongoDB
    mongo_task = mongo_tasks_connection.find_one({"task_id": task_id, "task": task})
    assert mongo_task is not None
    assert mongo_task["status"] == "success"
    assert mongo_task["code"] == 200
    assert mongo_task["import_name"] == "test_import"
    assert mongo_task["data"]["import_name"] == "test_import"


def test_update_task_id() -> None:
    """Test updating a task ID field in both Redis and MongoDB."""
    task_id = str(uuid4())
    task = "test_task"

    # First, set up a task
    initial_api_response = dtypes.ApiResponse(
        status="pending",
        code=202,
        message="Task started",
        data={"import_name": "test_import", "processing_status": "started"},
    )

    DatabaseTasksService.set_task_id(
        dtypes.SetTaskIdRequest(task_id=task_id, value=initial_api_response, task=task)
    )

    # Now update the task
    response = DatabaseTasksService.update_task_id(
        dtypes.UpdateTaskIdRequest(
            task_id=task_id,
            field="status",
            value="completed",
            task=task,
            message="Task completed successfully",
            data={"processing_status": "completed", "rows_processed": "1000"},
        )
    )

    # Assert the response
    assert response["success"] is True
    assert response["message"] == "Task updated successfully in both Redis and MongoDB"

    # Verify the update in Redis
    redis_task = redis_db.get_task_id(task_id, task)
    assert redis_task is not None
    assert redis_task["status"] == "completed"
    assert redis_task["message"] == "Task completed successfully"
    assert redis_task["data"]["processing_status"] == "completed"
    assert redis_task["data"]["rows_processed"] == "1000"

    # Verify the update in MongoDB
    mongo_task = mongo_tasks_connection.find_one({"task_id": task_id, "task": task})
    assert mongo_task is not None
    assert mongo_task["status"] == "completed"
    assert mongo_task["message"] == "Task completed successfully"


def test_get_task_id_from_redis() -> None:
    """Test getting a task ID that exists in Redis."""
    task_id = str(uuid4())
    task = "test_task"

    # Set up a task in Redis
    api_response = dtypes.ApiResponse(
        status="success",
        code=200,
        message="Task found in Redis",
        data={"import_name": "test_import", "source": "redis"},
    )

    redis_db.set_task_id(task_id, api_response, task)

    # Get the task
    response = DatabaseTasksService.get_task_id(
        dtypes.GetTaskIdRequest(task_id=task_id, task=task)
    )

    # Assert the response
    assert response["found"] is True
    assert response["value"] is not None
    assert response["value"]["status"] == "success"
    assert response["value"]["data"]["source"] == "redis"


def test_get_task_id_from_mongodb_fallback() -> None:
    """Test getting a task ID that exists only in MongoDB (Redis fallback)."""
    task_id = str(uuid4())
    task = "test_task"

    # Set up a task only in MongoDB
    mongo_document = {
        "task_id": task_id,
        "task": task,
        "import_name": "test_import",
        "status": "success",
        "code": 200,
        "message": "Task found in MongoDB",
        "data": {"import_name": "test_import", "source": "mongodb"},
    }

    mongo_tasks_connection.insert_one(mongo_document)

    # Get the task (should fallback to MongoDB since Redis is empty)
    response = DatabaseTasksService.get_task_id(
        dtypes.GetTaskIdRequest(task_id=task_id, task=task)
    )

    # Assert the response
    assert response["found"] is True
    assert response["value"] is not None
    assert response["value"]["status"] == "success"
    assert response["value"]["data"]["source"] == "mongodb"


def test_get_task_id_not_found() -> None:
    """Test getting a task ID that doesn't exist."""
    task_id = str(uuid4())
    task = "test_task"

    # Try to get a non-existent task
    response = DatabaseTasksService.get_task_id(
        dtypes.GetTaskIdRequest(task_id=task_id, task=task)
    )

    # Assert the response
    assert response["found"] is False
    assert response["value"] is None


def test_get_tasks_by_import_name_from_redis() -> None:
    """Test getting tasks by import name from Redis."""
    import_name = f"test_import_{uuid4()}"
    task = "test_task"

    # Set up multiple tasks in Redis with the same import_name
    for i in range(3):
        task_id = str(uuid4())
        api_response = dtypes.ApiResponse(
            status="success",
            code=200,
            message=f"Task {i + 1}",
            data={"import_name": import_name, "task_number": str(i + 1)},
        )
        redis_db.set_task_id(task_id, api_response, task)

    # Get tasks by import name
    response = DatabaseTasksService.get_tasks_by_import_name(
        dtypes.GetTasksByImportNameRequest(import_name=import_name, task=task)
    )

    # Assert the response
    assert len(response["tasks"]) == 3
    for task_data in response["tasks"]:
        assert task_data["status"] == "success"
        assert task_data["data"]["import_name"] == import_name


def test_get_tasks_by_import_name_from_mongodb_fallback() -> None:
    """Test getting tasks by import name from MongoDB (Redis fallback)."""
    import_name = f"mongodb_import_{uuid4()}"
    task = "test_task"

    # Set up multiple tasks only in MongoDB
    for i in range(2):
        task_id = str(uuid4())
        mongo_document = {
            "task_id": task_id,
            "task": task,
            "import_name": import_name,
            "status": "completed",
            "code": 200,
            "message": f"MongoDB Task {i + 1}",
            "data": {"import_name": import_name, "task_number": str(i + 1)},
        }
        mongo_tasks_connection.insert_one(mongo_document)

    # Get tasks by import name (should fallback to MongoDB)
    response = DatabaseTasksService.get_tasks_by_import_name(
        dtypes.GetTasksByImportNameRequest(import_name=import_name, task=task)
    )

    # Assert the response
    assert len(response["tasks"]) == 2
    for task_data in response["tasks"]:
        assert task_data["status"] == "completed"
        assert task_data["data"]["import_name"] == import_name


def test_get_tasks_by_import_name_empty_result() -> None:
    """Test getting tasks by import name when none exist."""
    import_name = "nonexistent_import"
    task = "test_task"

    # Try to get tasks for a non-existent import name
    response = DatabaseTasksService.get_tasks_by_import_name(
        dtypes.GetTasksByImportNameRequest(import_name=import_name, task=task)
    )

    # Assert the response
    assert len(response["tasks"]) == 0
