from proto_utils.database.mongo_serde import MongoSerde
from proto_utils.generated.database import mongo_pb2

from src.services.mongo import MongoSchemasService


class MongoHandler:
    @staticmethod
    def insert_one_schema(
        request: mongo_pb2.MongoInsertOneSchemaRequest,
    ) -> mongo_pb2.MongoInsertOneSchemaResponse:
        deserialized_request = MongoSerde.deserialize_insert_one_schema_request(request)
        service_response = MongoSchemasService.insert_one_schema(deserialized_request)
        return MongoSerde.serialize_insert_one_schema_response(service_response)

    @staticmethod
    def count_all_documents(
        request: mongo_pb2.MongoCountAllDocumentsRequest,
    ) -> mongo_pb2.MongoCountAllDocumentsResponse:
        deserialized_request = MongoSerde.deserialize_count_all_documents_request(
            request
        )
        service_response = MongoSchemasService.count_all_documents(deserialized_request)
        return MongoSerde.serialize_count_all_documents_response(service_response)

    @staticmethod
    def find_jsonschema(
        request: mongo_pb2.MongoFindJsonSchemaRequest,
    ) -> mongo_pb2.MongoFindJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_find_jsonschema_request(request)
        service_response = MongoSchemasService.find_one_jsonschema(deserialized_request)
        return MongoSerde.serialize_find_jsonschema_response(service_response)

    @staticmethod
    def update_one_jsonschema(
        request: mongo_pb2.MongoUpdateOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_update_one_jsonschema_request(
            request
        )
        service_response = MongoSchemasService.update_one_schema(deserialized_request)
        return MongoSerde.serialize_update_one_jsonschema_response(service_response)

    @staticmethod
    def delete_one_jsonschema(
        request: mongo_pb2.MongoDeleteOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaResponse:
        deserialized_request = MongoSerde.deserialize_delete_one_jsonschema_request(
            request
        )
        service_response = MongoSchemasService.delete_one_schema(deserialized_request)
        return MongoSerde.serialize_delete_one_jsonschema_response(service_response)

    @staticmethod
    def delete_import_name(
        request: mongo_pb2.MongoDeleteImportNameRequest,
    ) -> mongo_pb2.MongoDeleteImportNameResponse:
        deserialized_request = MongoSerde.deserialize_delete_import_name_request(
            request
        )
        service_response = MongoSchemasService.delete_import_name(deserialized_request)
        return MongoSerde.serialize_delete_import_name_response(service_response)
