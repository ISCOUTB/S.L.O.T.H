from fastapi import APIRouter, HTTPException, UploadFile, Depends
from messaging_utils.core.config import settings as mq_settings
from proto_utils.database import dtypes, DatabaseClient

from src.api.deps import get_db_client
from src.messaging.publisher import publisher

TASK = "validation"
router = APIRouter()


@router.post("/upload/{import_name}")
async def validate(
    spreadsheet_file: UploadFile,
    import_name: str,
    new: bool = False,
    database_client: DatabaseClient = Depends(get_db_client),
) -> dtypes.ApiResponse | list[dtypes.ApiResponse]:
    """
    Upload a spreadsheet file in order to be validated.
    """
    if not import_name:
        raise HTTPException(400, "import_name must be provided.")

    if not new and (
        cached_response := database_client.get_tasks_by_import_name(
            dtypes.GetTasksByImportNameRequest(import_name=import_name, task=TASK)
        )
    ):
        return cached_response["tasks"]

    try:
        # Read the file content
        file_content = await spreadsheet_file.read()

        # Metadata
        metadata = {
            "filename": spreadsheet_file.filename,
            "content_type": spreadsheet_file.content_type,
            "size": len(file_content),
        }

        # Publish in RabbitMQ
        # file_content = UploadFile(file_content)
        task_id = publisher.publish_validation_request(
            routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS,
            file_data=file_content,
            import_name=import_name,
            metadata=metadata,
            task="sample_validation",
        )

        response = dtypes.ApiResponse(
            status="accepted",
            code=202,
            message="Validation request submitted successfully",
            data={"task_id": task_id, "import_name": import_name},
        )

    except Exception as e:
        response = dtypes.ApiResponse(
            status="error",
            code=500,
            message=f"Failed to submit validation request: {str(e)}",
        )

    database_client.set_task_id(
        dtypes.SetTaskIdRequest(
            task_id=task_id,
            value=response,
            task=TASK,
        )
    )
    return response


@router.get("/status")
async def get_validation_status(
    task_id: str = "",
    import_name: str = "",
    database_client: DatabaseClient = Depends(get_db_client),
) -> dtypes.ApiResponse | list[dtypes.ApiResponse]:
    """
    Get the status of the file being validated.
    """
    if not task_id and not import_name:
        raise HTTPException(400, "Either `task_id` or `import_name` must be provided.")

    if import_name:
        cached_response = database_client.get_tasks_by_import_name(
            dtypes.GetTasksByImportNameRequest(import_name=import_name, task=TASK)
        )
        return cached_response["tasks"]

    cached_response = database_client.get_task_id(
        dtypes.GetTaskIdRequest(task_id=task_id, task=TASK)
    )
    if not cached_response["found"]:
        HTTPException(404, f"Task with ID {task_id} not found.")

    return cached_response["value"]
