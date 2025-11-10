import time
from typing import Callable

import pymongo.errors
import redis.exceptions
from proto_utils.database.database_serde import DatabaseSerde
from proto_utils.generated.database import database_pb2

from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection
from src.handlers.base import BaseHandler, Request, T
from src.services.tasks import DatabaseTasksService
from src.utils.logger import logger


class DatabaseTasksHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _execute_with_retry(
        self,
        operation: Callable[[Request, RedisConnection, MongoConnection], T],
        request: Request,
    ) -> T:
        max_retries = max(self.max_retries_redis, self.max_retries_mongo)
        retry_delay = max(self.retry_delay_redis, self.retry_delay_mongo)
        current_delay = retry_delay
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                force_reconnect = attempt > 1
                redis_db = self.manager.get_redis_connection(force_reconnect)
                mongo_db = self.manager.get_mongo_tasks_connection(force_reconnect)

                return operation(
                    request, redis_db=redis_db, mongo_tasks_connection=mongo_db
                )
            except (
                redis.exceptions.ConnectionError,
                redis.exceptions.TimeoutError,
                redis.exceptions.ResponseError,
                pymongo.errors.ConnectionFailure,
                pymongo.errors.ServerSelectionTimeoutError,
            ) as e:
                last_exception = e
                if attempt == max_retries:
                    logger.error(
                        f"Database operation '{operation.__name__}' failed after "
                        f"{max_retries} attempts: {e}"
                    )
                    raise

                logger.warning(
                    f"Database operation '{operation.__name__}' failed "
                    f"(attempt {attempt}/{max_retries}): {e}. "
                    f"Retrying in {current_delay}s..."
                )
                time.sleep(current_delay)
                current_delay *= self.backoff

        # just in case
        raise last_exception

    def update_task_id(
        self,
        request: database_pb2.UpdateTaskIdRequest,
    ) -> database_pb2.UpdateTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_update_task_id_request(request)
        service_response = self._execute_with_retry(
            DatabaseTasksService.update_task_id, deserialized_request
        )
        return DatabaseSerde.serialize_update_task_id_response(service_response)

    def get_task_id(
        self,
        request: database_pb2.GetTaskIdRequest,
    ) -> database_pb2.GetTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_get_task_id_request(request)
        service_response = self._execute_with_retry(
            DatabaseTasksService.get_task_id, deserialized_request
        )
        return DatabaseSerde.serialize_get_task_id_response(service_response)

    def get_tasks_by_import_name(
        self,
        request: database_pb2.GetTasksByImportNameRequest,
    ) -> database_pb2.GetTasksByImportNameResponse:
        deserialized_request = (
            DatabaseSerde.deserialize_get_tasks_by_import_name_request(request)
        )
        service_response = self._execute_with_retry(
            DatabaseTasksService.get_tasks_by_import_name, deserialized_request
        )

        return DatabaseSerde.serialize_get_tasks_by_import_name_response(
            service_response
        )

    def set_task_id(
        self,
        request: database_pb2.SetTaskIdRequest,
    ) -> database_pb2.SetTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_set_task_id_request(request)
        service_response = self._execute_with_retry(
            DatabaseTasksService.set_task_id, deserialized_request
        )
        return DatabaseSerde.serialize_set_task_id_response(service_response)
