import grpc
from proto_utils.database import dtypes
from proto_utils.database.mongo_serde import MongoSerde
from proto_utils.database.redis_serde import RedisSerde
from proto_utils.database.database_serde import DatabaseSerde
from proto_utils.generated.database.database_pb2_grpc import DatabaseServiceStub


class DatabaseClient:
    def __init__(self, channel: str) -> None:
        self.channel = grpc.insecure_channel(channel)
        self.stub = DatabaseServiceStub(self.channel)

    # ============================ Redis Methods ============================

    def redis_get_keys(
        self, request: dtypes.RedisGetKeysRequest
    ) -> dtypes.RedisGetKeysResponse:
        request_proto = RedisSerde.serialize_get_keys_request(request)
        response = self.stub.RedisGetKeys(request_proto)
        return RedisSerde.deserialize_get_keys_response(response)

    def redis_set(self, request: dtypes.RedisSetRequest) -> dtypes.RedisSetResponse:
        request_proto = RedisSerde.serialize_set_request(request)
        response = self.stub.RedisSet(request_proto)
        return RedisSerde.deserialize_set_response(response)

    def redis_get(self, request: dtypes.RedisGetRequest) -> dtypes.RedisGetResponse:
        request_proto = RedisSerde.serialize_get_request(request)
        response = self.stub.RedisGet(request_proto)
        return RedisSerde.deserialize_get_response(response)

    def redis_delete(
        self, request: dtypes.RedisDeleteRequest
    ) -> dtypes.RedisDeleteResponse:
        request_proto = RedisSerde.serialize_delete_request(request)
        response = self.stub.RedisDelete(request_proto)
        return RedisSerde.deserialize_delete_response(response)

    def redis_ping(
        self, request: dtypes.RedisPingRequest = None
    ) -> dtypes.RedisPingResponse:
        if request is None:
            request = dtypes.RedisPingRequest()
        request_proto = RedisSerde.serialize_ping_request(request)
        response = self.stub.RedisPing(request_proto)
        return RedisSerde.deserialize_ping_response(response)

    def redis_get_cache(
        self, request: dtypes.RedisGetCacheRequest = None
    ) -> dtypes.RedisGetCacheResponse:
        if request is None:
            request = dtypes.RedisGetCacheRequest()
        request_proto = RedisSerde.serialize_get_cache_request(request)
        response = self.stub.RedisGetCache(request_proto)
        return RedisSerde.deserialize_get_cache_response(response)

    def clear_cache(
        self, request: dtypes.RedisClearCacheRequest = None
    ) -> dtypes.RedisClearCacheResponse:
        if request is None:
            request = dtypes.RedisClearCacheRequest()
        request_proto = RedisSerde.serialize_clear_cache_request(request)
        response = self.stub.RedisClearCache(request_proto)
        return RedisSerde.deserialize_clear_cache_response(response)

    # ============================ Mongo Methods ============================

    def mongo_insert_one_schema(
        self, request: dtypes.MongoInsertOneSchemaRequest
    ) -> dtypes.MongoInsertOneSchemaResponse:
        request_proto = MongoSerde.serialize_insert_one_schema_request(request)
        response = self.stub.MongoInsertOneSchema(request_proto)
        return MongoSerde.deserialize_insert_one_schema_response(response)

    def mongo_count_all_documents(
        self, request: dtypes.MongoCountAllDocumentsRequest = None
    ) -> dtypes.MongoCountAllDocumentsResponse:
        if request is None:
            request = dtypes.MongoCountAllDocumentsRequest()
        request_proto = MongoSerde.serialize_count_all_documents_request(request)
        response = self.stub.MongoCountAllDocuments(request_proto)
        return MongoSerde.deserialize_count_all_documents_response(response)

    def mongo_find_jsonschema(
        self, request: dtypes.MongoFindJsonSchemaRequest
    ) -> dtypes.MongoFindJsonSchemaResponse:
        request_proto = MongoSerde.serialize_find_jsonschema_request(request)
        response = self.stub.MongoFindJsonSchema(request_proto)
        return MongoSerde.deserialize_find_jsonschema_response(response)

    def mongo_update_one_jsonschema(
        self, request: dtypes.MongoUpdateOneJsonSchemaRequest
    ) -> dtypes.MongoUpdateOneJsonSchemaResponse:
        request_proto = MongoSerde.serialize_update_one_jsonschema_request(request)
        response = self.stub.MongoUpdateOneJsonSchema(request_proto)
        return MongoSerde.deserialize_update_one_jsonschema_response(response)

    def mongo_delete_one_jsonschema(
        self, request: dtypes.MongoDeleteOneJsonSchemaRequest
    ) -> dtypes.MongoDeleteOneJsonSchemaResponse:
        request_proto = MongoSerde.serialize_delete_one_jsonschema_request(request)
        response = self.stub.MongoDeleteOneJsonSchema(request_proto)
        return MongoSerde.deserialize_delete_one_jsonschema_response(response)

    def mongo_delete_import_name(
        self, request: dtypes.MongoDeleteImportNameRequest
    ) -> dtypes.MongoDeleteImportNameResponse:
        request_proto = MongoSerde.serialize_delete_import_name_request(request)
        response = self.stub.MongoDeleteImportName(request_proto)
        return MongoSerde.deserialize_delete_import_name_response(response)

    # ============================ Tasks Methods ============================

    def update_task_id(
        self, request: dtypes.UpdateTaskIdRequest
    ) -> dtypes.UpdateTaskIdResponse:
        request_proto = DatabaseSerde.serialize_update_task_id_request(request)
        response = self.stub.UpdateTaskId(request_proto)
        return DatabaseSerde.deserialize_update_task_id_response(response)

    def get_task_id(self, request: dtypes.GetTaskIdRequest) -> dtypes.GetTaskIdResponse:
        request_proto = DatabaseSerde.serialize_get_task_id_request(request)
        response = self.stub.GetTaskId(request_proto)
        return DatabaseSerde.deserialize_get_task_id_response(response)

    def get_tasks_by_import_name(
        self, request: dtypes.GetTasksByImportNameRequest
    ) -> dtypes.GetTasksByImportNameResponse:
        request_proto = DatabaseSerde.serialize_get_tasks_by_import_name_request(
            request
        )
        response = self.stub.GetTasksByImportName(request_proto)
        return DatabaseSerde.deserialize_get_tasks_by_import_name_response(response)

    def set_task_id(self, request: dtypes.SetTaskIdRequest) -> dtypes.SetTaskIdResponse:
        request_proto = DatabaseSerde.serialize_set_task_id_request(request)
        response = self.stub.SetTaskId(request_proto)
        return DatabaseSerde.deserialize_set_task_id_response(response)
