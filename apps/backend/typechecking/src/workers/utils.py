from typing import Any, Dict, Optional

from proto_utils.database import dtypes

from src.core.database_client import DatabaseClient


def update_task_status(
    *,
    task_id: str,
    field: str,
    value: Any,
    task: str,
    database_client: Optional[DatabaseClient] = None,
    message: str = "",
    data: Optional[Dict[str, str]] = None,
    reset_data: bool = False,
) -> None:
    """Update the status of a task in the database.

    Args:
        task_id (str): The unique identifier of the task.
        field (str): The field to update (e.g., "status", "progress").
        value (Any): The new value for the specified field.
        task (str): The type of task (e.g., "schema_validation").
        database_client (Optional[DatabaseClient]): The database client to use.
            If None, a default client will be used.
        message (str): An optional message to include with the update.
        data (Optional[Dict[str, str]]): Additional data to attach to the task.
        reset_data (bool): Whether to reset existing data for the task.

    Returns:
        None: This function does not return a value.
    """
    database_client.update_task_id(
        dtypes.UpdateTaskIdRequest(
            task_id=task_id,
            field=field,
            value=value,
            task=task,
            message=message,
            data=data,
            reset_data=reset_data,
        )
    )
