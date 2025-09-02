from typing import Any
from src.core.database_redis import redis_db
from src.core.database_mongo import mongo_connection  # noqa: F401


def update_task_status(
    task_id: str,
    field: str,
    value: Any,
    task: str,
    *,
    message: str = "",
    data: dict | None = None,
    reset_data: bool = False,
) -> None:
    # Update task in redis
    redis_db.update_task_id(
        task_id=task_id,
        field=field,
        value=value,
        task=task,
        message=message,
        data=data,
        reset_data=reset_data,
    )

    # TODO: Update task in Mongo
    # Goes right here...
