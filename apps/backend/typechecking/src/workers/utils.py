from typing import Any, Dict, Optional

from proto_utils.database import dtypes

from src.core.database_client import database_client


def update_task_status(
    task_id: str,
    field: str,
    value: Any,
    task: str,
    *,
    message: str = "",
    data: Optional[Dict[str, str]] = None,
    reset_data: bool = False,
) -> None:
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
