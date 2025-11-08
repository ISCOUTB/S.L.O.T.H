import time
import logging
from typing import Callable, Optional, TypeVar

import grpc
from proto_utils.database import dtypes
from proto_utils.database.mongo_serde import MongoSerde
from proto_utils.database.redis_serde import RedisSerde
from proto_utils.database.database_serde import DatabaseSerde
from proto_utils.generated.database.database_pb2_grpc import DatabaseServiceStub

T = TypeVar("T")


class DatabaseClient:
    def __init__(
        self,
        channel_address: str,
        max_retries: int,
        retry_delay: float,
        backoff: float,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the DatabaseClient with retry configuration.

        Args:
            channel_address (str): gRPC server address (host:port).
            max_retries (int): Maximum number of retry attempts.
            retry_delay (float): Initial delay between retries in seconds.
            backoff (float): Multiplier for exponential backoff.
            logger (Optional[logging.Logger]): Optional logger for logging messages.
        """
        self._channel_address = channel_address
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff = backoff

        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[DatabaseServiceStub] = None
        self._initialize_channel()

    def close(self) -> None:
        """Close the gRPC channel.

        Safely closes the channel if it exists. Should be called when
        the client is no longer needed to release resources.
        """
        self._channel.close()

    def _initialize_channel(self) -> None:
        """Initialize or reinitialize the gRPC channel and stub.

        Creates a new insecure channel to the database service and
        initializes the stub for making RPC calls.
        """
        if self._channel:
            try:
                self.close()
            except Exception:
                pass

        self._channel = grpc.insecure_channel(self._channel_address)
        self._stub = DatabaseServiceStub(self._channel)

    def _execute_with_retry(self, operation: Callable[[], T], operation_name: str) -> T:
        """Execute a gRPC operation with automatic retry on failure.

        This method wraps gRPC operations with retry logic that handles
        connection failures. It uses exponential backoff between retries
        and automatically reinitializes the channel on failures.

        Args:
            operation: Callable that performs the gRPC operation.
            operation_name: Name of the operation for logging purposes.

        Returns:
            T: Result of the gRPC operation.

        Raises:
            grpc.RpcError: The last gRPC error encountered if all retries
                are exhausted.

        Retry Logic:
            - First attempt uses existing channel
            - Subsequent attempts reinitialize the channel
            - Delay increases exponentially: delay * (backoff ^ attempt)
            - Handles all gRPC errors (connectivity, unavailable, etc.)
        """
        current_delay = self.retry_delay
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Reinitialize channel on retries
                if attempt > 1:
                    self.logger.info(
                        f"[DatabaseClient] Reinitializing channel for {operation_name} "
                        f"(attempt {attempt}/{self.max_retries})"
                    )
                    self._initialize_channel()

                # Execute the operation
                return operation()

            except grpc.RpcError as e:
                last_exception = e

                if attempt == self.max_retries:
                    self.logger.warning(
                        f"[DatabaseClient] {operation_name} failed after "
                        f"{self.max_retries} attempts: {e.code()} - {e.details()}"
                    )
                    raise

                self.logger.warning(
                    f"[DatabaseClient] {operation_name} failed "
                    f"(attempt {attempt}/{self.max_retries}): "
                    f"{e.code()} - {e.details()}. "
                    f"Retrying in {current_delay}s..."
                )
                time.sleep(current_delay)
                current_delay *= self.backoff

        # Should never reach here, but just in case
        raise last_exception

    # ============================ Redis Methods ============================

    def redis_get_keys(
        self, request: dtypes.RedisGetKeysRequest
    ) -> dtypes.RedisGetKeysResponse:
        def _operation() -> dtypes.RedisGetKeysResponse:
            request_proto = RedisSerde.serialize_get_keys_request(request)
            response = self._stub.RedisGetKeys(request_proto)
            return RedisSerde.deserialize_get_keys_response(response)

        return self._execute_with_retry(_operation, "RedisGetKeys")

    def redis_set(self, request: dtypes.RedisSetRequest) -> dtypes.RedisSetResponse:
        def _operation() -> dtypes.RedisSetResponse:
            request_proto = RedisSerde.serialize_set_request(request)
            response = self._stub.RedisSet(request_proto)
            return RedisSerde.deserialize_set_response(response)

        return self._execute_with_retry(_operation, "RedisSet")

    def redis_get(self, request: dtypes.RedisGetRequest) -> dtypes.RedisGetResponse:
        def _operation() -> dtypes.RedisGetResponse:
            request_proto = RedisSerde.serialize_get_request(request)
            response = self._stub.RedisGet(request_proto)
            return RedisSerde.deserialize_get_response(response)

        return self._execute_with_retry(_operation, "RedisGet")

    def redis_delete(
        self, request: dtypes.RedisDeleteRequest
    ) -> dtypes.RedisDeleteResponse:
        def _operation() -> dtypes.RedisDeleteResponse:
            request_proto = RedisSerde.serialize_delete_request(request)
            response = self._stub.RedisDelete(request_proto)
            return RedisSerde.deserialize_delete_response(response)

        return self._execute_with_retry(_operation, "RedisDelete")

    def redis_ping(
        self, request: dtypes.RedisPingRequest = None
    ) -> dtypes.RedisPingResponse:
        def _operation() -> dtypes.RedisPingResponse:
            local_request = request
            if local_request is None:
                local_request = dtypes.RedisPingRequest()
            request_proto = RedisSerde.serialize_ping_request(local_request)
            response = self._stub.RedisPing(request_proto)
            return RedisSerde.deserialize_ping_response(response)

        return self._execute_with_retry(_operation, "RedisPing")

    def redis_get_cache(
        self, request: dtypes.RedisGetCacheRequest = None
    ) -> dtypes.RedisGetCacheResponse:
        def _operation() -> dtypes.RedisGetCacheResponse:
            local_request = request
            if local_request is None:
                local_request = dtypes.RedisGetCacheRequest()
            request_proto = RedisSerde.serialize_get_cache_request(local_request)
            response = self._stub.RedisGetCache(request_proto)
            return RedisSerde.deserialize_get_cache_response(response)

        return self._execute_with_retry(_operation, "RedisGetCache")

    def clear_cache(
        self, request: dtypes.RedisClearCacheRequest = None
    ) -> dtypes.RedisClearCacheResponse:
        def _operation() -> dtypes.RedisClearCacheResponse:
            local_request = request
            if local_request is None:
                local_request = dtypes.RedisClearCacheRequest()
            request_proto = RedisSerde.serialize_clear_cache_request(local_request)
            response = self._stub.RedisClearCache(request_proto)
            return RedisSerde.deserialize_clear_cache_response(response)

        return self._execute_with_retry(_operation, "RedisClearCache")

    # ============================ Mongo Methods ============================

    def mongo_ping(
        self, request: dtypes.MongoPingRequest = None
    ) -> dtypes.MongoPingResponse:
        def _operation() -> dtypes.MongoPingResponse:
            request_proto = MongoSerde.serialize_ping_request(request)
            response = self._stub.MongoPing(request_proto)
            return MongoSerde.deserialize_ping_response(response)

        return self._execute_with_retry(_operation, "MongoPing")

    def mongo_insert_one_schema(
        self, request: dtypes.MongoInsertOneSchemaRequest
    ) -> dtypes.MongoInsertOneSchemaResponse:
        def _operation() -> dtypes.MongoInsertOneSchemaResponse:
            request_proto = MongoSerde.serialize_insert_one_schema_request(request)
            response = self._stub.MongoInsertOneSchema(request_proto)
            return MongoSerde.deserialize_insert_one_schema_response(response)

        return self._execute_with_retry(_operation, "MongoInsertOneSchema")

    def mongo_count_all_documents(
        self, request: dtypes.MongoCountAllDocumentsRequest = None
    ) -> dtypes.MongoCountAllDocumentsResponse:
        def _operation() -> dtypes.MongoCountAllDocumentsResponse:
            local_request = request
            if local_request is None:
                local_request = dtypes.MongoCountAllDocumentsRequest()
            request_proto = MongoSerde.serialize_count_all_documents_request(
                local_request
            )
            response = self._stub.MongoCountAllDocuments(request_proto)
            return MongoSerde.deserialize_count_all_documents_response(response)

        return self._execute_with_retry(_operation, "MongoCountAllDocuments")

    def mongo_find_jsonschema(
        self, request: dtypes.MongoFindJsonSchemaRequest
    ) -> dtypes.MongoFindJsonSchemaResponse:
        def _operation() -> dtypes.MongoFindJsonSchemaResponse:
            request_proto = MongoSerde.serialize_find_jsonschema_request(request)
            response = self._stub.MongoFindJsonSchema(request_proto)
            return MongoSerde.deserialize_find_jsonschema_response(response)

        return self._execute_with_retry(_operation, "MongoFindJsonSchema")

    def mongo_update_one_jsonschema(
        self, request: dtypes.MongoUpdateOneJsonSchemaRequest
    ) -> dtypes.MongoUpdateOneJsonSchemaResponse:
        def _operation() -> dtypes.MongoUpdateOneJsonSchemaResponse:
            request_proto = MongoSerde.serialize_update_one_jsonschema_request(request)
            response = self._stub.MongoUpdateOneJsonSchema(request_proto)
            return MongoSerde.deserialize_update_one_jsonschema_response(response)

        return self._execute_with_retry(_operation, "MongoUpdateOneJsonSchema")

    def mongo_delete_one_jsonschema(
        self, request: dtypes.MongoDeleteOneJsonSchemaRequest
    ) -> dtypes.MongoDeleteOneJsonSchemaResponse:
        def _operation() -> dtypes.MongoDeleteOneJsonSchemaResponse:
            request_proto = MongoSerde.serialize_delete_one_jsonschema_request(request)
            response = self._stub.MongoDeleteOneJsonSchema(request_proto)
            return MongoSerde.deserialize_delete_one_jsonschema_response(response)

        return self._execute_with_retry(_operation, "MongoDeleteOneJsonSchema")

    def mongo_delete_import_name(
        self, request: dtypes.MongoDeleteImportNameRequest
    ) -> dtypes.MongoDeleteImportNameResponse:
        def _operation() -> dtypes.MongoDeleteImportNameResponse:
            request_proto = MongoSerde.serialize_delete_import_name_request(request)
            response = self._stub.MongoDeleteImportName(request_proto)
            return MongoSerde.deserialize_delete_import_name_response(response)

        return self._execute_with_retry(_operation, "MongoDeleteImportName")

    # ============================ Tasks Methods ============================

    def update_task_id(
        self, request: dtypes.UpdateTaskIdRequest
    ) -> dtypes.UpdateTaskIdResponse:
        def _operation() -> dtypes.UpdateTaskIdResponse:
            request_proto = DatabaseSerde.serialize_update_task_id_request(request)
            response = self._stub.UpdateTaskId(request_proto)
            return DatabaseSerde.deserialize_update_task_id_response(response)

        return self._execute_with_retry(_operation, "UpdateTaskId")

    def get_task_id(self, request: dtypes.GetTaskIdRequest) -> dtypes.GetTaskIdResponse:
        def _operation() -> dtypes.GetTaskIdResponse:
            request_proto = DatabaseSerde.serialize_get_task_id_request(request)
            response = self._stub.GetTaskId(request_proto)
            return DatabaseSerde.deserialize_get_task_id_response(response)

        return self._execute_with_retry(_operation, "GetTaskId")

    def get_tasks_by_import_name(
        self, request: dtypes.GetTasksByImportNameRequest
    ) -> dtypes.GetTasksByImportNameResponse:
        def _operation() -> dtypes.GetTasksByImportNameResponse:
            request_proto = DatabaseSerde.serialize_get_tasks_by_import_name_request(
                request
            )
            response = self._stub.GetTasksByImportName(request_proto)
            return DatabaseSerde.deserialize_get_tasks_by_import_name_response(response)

        return self._execute_with_retry(_operation, "GetTasksByImportName")

    def set_task_id(self, request: dtypes.SetTaskIdRequest) -> dtypes.SetTaskIdResponse:
        def _operation() -> dtypes.SetTaskIdResponse:
            request_proto = DatabaseSerde.serialize_set_task_id_request(request)
            response = self._stub.SetTaskId(request_proto)
            return DatabaseSerde.deserialize_set_task_id_response(response)

        return self._execute_with_retry(_operation, "SetTaskId")
