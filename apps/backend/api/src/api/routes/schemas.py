from fastapi import APIRouter
from fastapi import HTTPException

from src.schemas.messaging import ApiResponse
from src.messaging.publishers import ValidationPublisher
from src.core.database_redis import redis_db

TASK = "schemas"
router = APIRouter()
publisher = ValidationPublisher()


@router.post("/upload/{import_name}")
async def upload_schema(
    import_name: str,
    schema: dict,
    raw: bool = False,
    new: bool = False,
) -> ApiResponse | list[ApiResponse]:
    """
    Upload a schema for validation.
    This endpoint allows users to upload a JSON schema for validation purposes.
    It checks if the schema is the same as the active schema in the database.
    If it is the same, no update is made. If it is different, the schema is saved
    as the active schema and added to the schemas_releases.
    """
    if not import_name:
        raise HTTPException(400, "import_name must be provided.")

    if not new and (
        cached_response := redis_db.get_tasks_by_import_name(
            import_name, task=TASK
        )
    ):
        return cached_response

    try:
        task_id = publisher.publish_schema_update(
            schema=schema, import_name=import_name, raw=raw, task="upload_schema"
        )

        response = ApiResponse(
            status="accepted",
            code=202,
            message="Schema upload request submitted successfully",
            data={"task_id": task_id, "import_name": import_name},
        )
    except Exception as e:
        task_id = None
        response = ApiResponse(
            status="error",
            code=500,
            message=f"Failed to upload schema: {str(e)}",
            data={"task_id": task_id, "import_name": import_name},
        )

    redis_db.set_task_id(task_id, response.copy(), task=TASK)
    return response


@router.get("/status")
async def get_schema_task(
    task_id: str = "", import_name: str = ""
) -> list[ApiResponse] | ApiResponse:
    """
    Get the status of a schema upload task.
    This endpoint retrieves the status of a schema upload task by its ID.
    """
    if not task_id and not import_name:
        raise HTTPException(400, "Either task_id or import_name must be provided.")

    if import_name:
        tasks = redis_db.get_tasks_by_import_name(import_name, task=TASK)
        return tasks

    cached_response = redis_db.get_task_id(task_id, task=TASK)
    if not cached_response:
        raise HTTPException(404, f"Task with ID {task_id} not found.")

    return cached_response


@router.delete("/remove/{import_name}")
async def remove_schema(
    import_name: str,
) -> ApiResponse:
    """
    Remove a schema by its import name.
    This endpoint allows users to remove a schema from the system by its import name.
    It publishes a message to remove the schema and returns the task ID for tracking.
    """
    if not import_name:
        raise HTTPException(400, "import_name must be provided.")

    try:
        task_id = publisher.publish_schema_update(
            import_name=import_name, task="remove_schema"
        )

        response = ApiResponse(
            status="accepted",
            code=202,
            message="Schema removal request submitted successfully",
            data={"task_id": task_id, "import_name": import_name},
        )
    except Exception as e:
        response = ApiResponse(
            status="error",
            code=500,
            message=f"Failed to remove schema: {str(e)}",
        )

    redis_db.set_task_id(task_id, response.copy(), task=TASK)
    return response
