import time
from typing import Callable

import pymongo.errors
from proto_utils.database.mongo_serde import MongoSerde
from proto_utils.generated.database import mongo_pb2

from src.core.database_mongo import MongoConnection
from src.handlers.base import BaseHandler, Request, T
from src.services.mongo import MongoSchemasService


class MongoHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _execute_with_retry(
        self,
        operation: Callable[[Request, MongoConnection], T],
        request: Request,
    ) -> T:
        current_delay = self.retry_delay_mongo
        last_exception = None

        for attempt in range(1, self.max_retries_mongo + 1):
            try:
                mongo_db = self.manager.get_mongo_schemas_connection(attempt > 1)
                return operation(request, mongo_schemas_connection=mongo_db)
            except (
                pymongo.errors.ConnectionFailure,
                pymongo.errors.ServerSelectionTimeoutError,
            ) as e:
                last_exception = e
                if attempt == self.max_retries_mongo:
                    raise

                time.sleep(current_delay)
                current_delay *= self.backoff_mongo

        # just in case
        raise last_exception

    def ping(self, request: mongo_pb2.MongoPingRequest) -> mongo_pb2.MongoPingResponse:
        deserialized_request = MongoSerde.deserialize_ping_request(request)
        service_response = self._execute_with_retry(
            MongoSchemasService.ping, deserialized_request
        )
        return MongoSerde.serialize_ping_response(service_response)

    def insert_one_schema(
        self,
        request: mongo_pb2.MongoInsertOneSchemaRequest,
    ) -> mongo_pb2.MongoInsertOneSchemaResponse:
        deserialized_request = MongoSerde.deserialize_insert_one_schema_request(request)

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.insert_one_schema(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_insert_one_schema_response(service_response)

    def count_all_documents(
        self,
        request: mongo_pb2.MongoCountAllDocumentsRequest,
    ) -> mongo_pb2.MongoCountAllDocumentsResponse:
        deserialized_request = MongoSerde.deserialize_count_all_documents_request(
            request
        )

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.count_all_documents(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_count_all_documents_response(service_response)

    def find_jsonschema(
        self,
        request: mongo_pb2.MongoFindJsonSchemaRequest,
    ) -> mongo_pb2.MongoFindJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_find_jsonschema_request(request)

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.find_one_jsonschema(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_find_jsonschema_response(service_response)

    def update_one_jsonschema(
        self,
        request: mongo_pb2.MongoUpdateOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_update_one_jsonschema_request(
            request
        )

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.update_one_schema(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_update_one_jsonschema_response(service_response)

    def delete_one_jsonschema(
        self,
        request: mongo_pb2.MongoDeleteOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_delete_one_jsonschema_request(
            request
        )

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.delete_one_schema(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_delete_one_jsonschema_response(service_response)

    def delete_import_name(
        self,
        request: mongo_pb2.MongoDeleteImportNameRequest,
    ) -> mongo_pb2.MongoDeleteImportNameResponse:
        deserialized_request = MongoSerde.deserialize_delete_import_name_request(
            request
        )

        def operation(req, *, mongo_schemas_connection):
            return MongoSchemasService.delete_import_name(
                req, mongo_schemas_connection=mongo_schemas_connection
            )

        service_response = self._execute_with_retry(operation, deserialized_request)
        return MongoSerde.serialize_delete_import_name_response(service_response)
