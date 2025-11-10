"""MongoDB serialization and deserialization module.

This module provides serialization and deserialization utilities for MongoDB
operations specifically focused on JSON schema storage, retrieval, and management.
Contains the MongoSerde class with methods for converting between Python dictionaries
and Protocol Buffer messages for MongoDB schema operations.
"""

from proto_utils.database import dtypes
from proto_utils.database.utils_serde import DatabaseUtilsSerde
from proto_utils.generated.database import mongo_pb2


class MongoSerde:
    """Serialization and deserialization utilities for MongoDB schema operations.

    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    MongoDB operations. Focuses specifically on JSON schema management including
    storage, retrieval, updates, and version tracking.
    """

    @staticmethod
    def serialize_ping_request(
        request: dtypes.MongoPingRequest = None,
    ) -> mongo_pb2.MongoPingRequest:
        """Serialize a MongoPingRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB ping request dictionary to serialize (optional).

        Returns:
            The serialized Protocol Buffer MongoPingRequest message.
        """
        return mongo_pb2.MongoPingRequest()

    @staticmethod
    def deserialize_ping_request(
        proto: mongo_pb2.MongoPingRequest,
    ) -> dtypes.MongoPingRequest:
        """Deserialize a Protocol Buffer MongoPingRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoPingRequest message to deserialize.

        Returns:
            The deserialized MongoDB ping request dictionary.
        """
        return dtypes.MongoPingRequest()

    def serialize_ping_response(
        response: dtypes.MongoPingResponse,
    ) -> mongo_pb2.MongoPingResponse:
        """Serialize a MongoPingResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB ping response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoPingResponse message.
        """
        return mongo_pb2.MongoPingResponse(
            pong=response["pong"],
        )

    @staticmethod
    def deserialize_ping_response(
        proto: mongo_pb2.MongoPingResponse,
    ) -> dtypes.MongoPingResponse:
        """Deserialize a Protocol Buffer MongoPingResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoPingResponse message to deserialize.

        Returns:
            The deserialized MongoDB ping response dictionary.
        """
        return dtypes.MongoPingResponse(
            pong=proto.pong,
        )

    @staticmethod
    def serialize_insert_one_schema_request(
        request: dtypes.MongoInsertOneSchemaRequest,
    ) -> mongo_pb2.MongoInsertOneSchemaRequest:
        """Serialize a MongoInsertOneSchemaRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB insert one schema request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoInsertOneSchemaRequest message.
        """
        return mongo_pb2.MongoInsertOneSchemaRequest(
            import_name=request["import_name"],
            created_at=request["created_at"],
            active_schema=DatabaseUtilsSerde.serialize_jsonschema(
                request["active_schema"]
            ),
            schemas_releases=list(
                map(
                    lambda schema: DatabaseUtilsSerde.serialize_jsonschema(schema),
                    request["schemas_releases"],
                )
            ),
        )

    @staticmethod
    def deserialize_insert_one_schema_request(
        proto: mongo_pb2.MongoInsertOneSchemaRequest,
    ) -> dtypes.MongoInsertOneSchemaRequest:
        """Deserialize a Protocol Buffer MongoInsertOneSchemaRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoInsertOneSchemaRequest message to deserialize.

        Returns:
            The deserialized MongoDB insert one schema request dictionary.
        """
        return dtypes.MongoInsertOneSchemaRequest(
            import_name=proto.import_name,
            created_at=proto.created_at,
            active_schema=DatabaseUtilsSerde.deserialize_jsonschema(
                proto.active_schema
            ),
            schemas_releases=list(
                map(
                    lambda schema: DatabaseUtilsSerde.deserialize_jsonschema(schema),
                    proto.schemas_releases,
                )
            ),
        )

    @staticmethod
    def serialize_insert_one_schema_response(
        response: dtypes.MongoInsertOneSchemaResponse,
    ) -> mongo_pb2.MongoInsertOneSchemaResponse:
        """Serialize a MongoInsertOneSchemaResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB insert one schema response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoInsertOneSchemaResponse message.
        """
        return mongo_pb2.MongoInsertOneSchemaResponse(
            status=response["status"],
            result=response["result"],
        )

    @staticmethod
    def deserialize_insert_one_schema_response(
        proto: mongo_pb2.MongoInsertOneSchemaResponse,
    ) -> dtypes.MongoInsertOneSchemaResponse:
        """Deserialize a Protocol Buffer MongoInsertOneSchemaResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoInsertOneSchemaResponse message to deserialize.

        Returns:
            The deserialized MongoDB insert one schema response dictionary.
        """
        return dtypes.MongoInsertOneSchemaResponse(
            status=proto.status,
            result=dict(proto.result),
        )

    @staticmethod
    def serialize_count_all_documents_request(
        request: dtypes.MongoCountAllDocumentsRequest = None,
    ) -> mongo_pb2.MongoCountAllDocumentsRequest:
        """Serialize a MongoCountAllDocumentsRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB count all documents request dictionary to serialize (optional).

        Returns:
            The serialized Protocol Buffer MongoCountAllDocumentsRequest message.
        """
        return mongo_pb2.MongoCountAllDocumentsRequest()

    @staticmethod
    def deserialize_count_all_documents_request(
        proto: mongo_pb2.MongoCountAllDocumentsRequest,
    ) -> dtypes.MongoCountAllDocumentsRequest:
        """Deserialize a Protocol Buffer MongoCountAllDocumentsRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoCountAllDocumentsRequest message to deserialize.

        Returns:
            The deserialized MongoDB count all documents request dictionary.
        """
        return dtypes.MongoCountAllDocumentsRequest()

    @staticmethod
    def serialize_count_all_documents_response(
        response: dtypes.MongoCountAllDocumentsResponse,
    ) -> mongo_pb2.MongoCountAllDocumentsResponse:
        """Serialize a MongoCountAllDocumentsResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB count all documents response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoCountAllDocumentsResponse message.
        """
        return mongo_pb2.MongoCountAllDocumentsResponse(
            amount=response["amount"],
        )

    @staticmethod
    def deserialize_count_all_documents_response(
        proto: mongo_pb2.MongoCountAllDocumentsResponse,
    ) -> dtypes.MongoCountAllDocumentsResponse:
        """Deserialize a Protocol Buffer MongoCountAllDocumentsResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoCountAllDocumentsResponse message to deserialize.

        Returns:
            The deserialized MongoDB count all documents response dictionary.
        """
        return dtypes.MongoCountAllDocumentsResponse(
            amount=proto.amount,
        )

    @staticmethod
    def serialize_find_jsonschema_request(
        request: dtypes.MongoFindJsonSchemaRequest,
    ) -> mongo_pb2.MongoFindJsonSchemaRequest:
        """Serialize a MongoFindJsonSchemaRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB find JSON schema request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoFindJsonSchemaRequest message.
        """
        return mongo_pb2.MongoFindJsonSchemaRequest(import_name=request["import_name"])

    @staticmethod
    def deserialize_find_jsonschema_request(
        proto: mongo_pb2.MongoFindJsonSchemaRequest,
    ) -> dtypes.MongoFindJsonSchemaRequest:
        """Deserialize a Protocol Buffer MongoFindJsonSchemaRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoFindJsonSchemaRequest message to deserialize.

        Returns:
            The deserialized MongoDB find JSON schema request dictionary.
        """
        return dtypes.MongoFindJsonSchemaRequest(
            import_name=proto.import_name,
        )

    @staticmethod
    def serialize_find_jsonschema_response(
        response: dtypes.MongoFindJsonSchemaResponse,
    ) -> mongo_pb2.MongoFindJsonSchemaResponse:
        """Serialize a MongoFindJsonSchemaResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB find JSON schema response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoFindJsonSchemaResponse message.
        """
        # Handle None schema case (when schema is not found)
        schema_proto = None
        if response["schema"] is not None:
            schema_proto = DatabaseUtilsSerde.serialize_jsonschema(response["schema"])

        return mongo_pb2.MongoFindJsonSchemaResponse(
            status=response["status"],
            extra=response["extra"],
            schema=schema_proto,
        )

    @staticmethod
    def deserialize_find_jsonschema_response(
        proto: mongo_pb2.MongoFindJsonSchemaResponse,
    ) -> dtypes.MongoFindJsonSchemaResponse:
        """Deserialize a Protocol Buffer MongoFindJsonSchemaResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoFindJsonSchemaResponse message to deserialize.

        Returns:
            The deserialized MongoDB find JSON schema response dictionary.
        """
        return dtypes.MongoFindJsonSchemaResponse(
            status=proto.status,
            extra=dict(proto.extra),
            schema=DatabaseUtilsSerde.deserialize_jsonschema(proto.schema),
        )

    @staticmethod
    def serialize_update_one_jsonschema_request(
        request: dtypes.MongoUpdateOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaRequest:
        """Serialize a MongoUpdateOneJsonSchemaRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB update one JSON schema request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoUpdateOneJsonSchemaRequest message.
        """
        return mongo_pb2.MongoUpdateOneJsonSchemaRequest(
            import_name=request["import_name"],
            schema=DatabaseUtilsSerde.serialize_jsonschema(request["schema"]),
            created_at=request["created_at"],
        )

    @staticmethod
    def deserialize_update_one_jsonschema_request(
        proto: mongo_pb2.MongoUpdateOneJsonSchemaRequest,
    ) -> dtypes.MongoUpdateOneJsonSchemaRequest:
        """Deserialize a Protocol Buffer MongoUpdateOneJsonSchemaRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoUpdateOneJsonSchemaRequest message to deserialize.

        Returns:
            The deserialized MongoDB update one JSON schema request dictionary.
        """
        return dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=proto.import_name,
            schema=DatabaseUtilsSerde.deserialize_jsonschema(proto.schema),
            created_at=proto.created_at,
        )

    @staticmethod
    def serialize_update_one_jsonschema_response(
        response: dtypes.MongoUpdateOneJsonSchemaResponse,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaResponse:
        """Serialize a MongoUpdateOneJsonSchemaResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB update one JSON schema response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoUpdateOneJsonSchemaResponse message.
        """
        return mongo_pb2.MongoUpdateOneJsonSchemaResponse(
            status=response["status"],
            result=response["result"],
        )

    @staticmethod
    def deserialize_update_one_jsonschema_response(
        proto: mongo_pb2.MongoUpdateOneJsonSchemaResponse,
    ) -> dtypes.MongoUpdateOneJsonSchemaResponse:
        """Deserialize a Protocol Buffer MongoUpdateOneJsonSchemaResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoUpdateOneJsonSchemaResponse message to deserialize.

        Returns:
            The deserialized MongoDB update one JSON schema response dictionary.
        """
        return dtypes.MongoUpdateOneJsonSchemaResponse(
            status=proto.status,
            result=dict(proto.result),
        )

    @staticmethod
    def serialize_delete_one_jsonschema_request(
        request: dtypes.MongoDeleteOneJsonSchemaRequest,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaRequest:
        """Serialize a MongoDeleteOneJsonSchemaRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB delete one JSON schema request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoDeleteOneJsonSchemaRequest message.
        """
        return mongo_pb2.MongoDeleteOneJsonSchemaRequest(
            import_name=request["import_name"],
        )

    @staticmethod
    def deserialize_delete_one_jsonschema_request(
        proto: mongo_pb2.MongoDeleteOneJsonSchemaRequest,
    ) -> dtypes.MongoDeleteOneJsonSchemaRequest:
        """Deserialize a Protocol Buffer MongoDeleteOneJsonSchemaRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoDeleteOneJsonSchemaRequest message to deserialize.

        Returns:
            The deserialized MongoDB delete one JSON schema request dictionary.
        """
        return dtypes.MongoDeleteOneJsonSchemaRequest(
            import_name=proto.import_name,
        )

    @staticmethod
    def serialize_delete_one_jsonschema_response(
        response: dtypes.MongoDeleteOneJsonSchemaResponse,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaResponse:
        """Serialize a MongoDeleteOneJsonSchemaResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB delete one JSON schema response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoDeleteOneJsonSchemaResponse message.
        """
        return mongo_pb2.MongoDeleteOneJsonSchemaResponse(
            success=response["success"],
            message=response["message"],
            status=response["status"],
            extra=response["extra"],
        )

    @staticmethod
    def deserialize_delete_one_jsonschema_response(
        proto: mongo_pb2.MongoDeleteOneJsonSchemaResponse,
    ) -> dtypes.MongoDeleteOneJsonSchemaResponse:
        """Deserialize a Protocol Buffer MongoDeleteOneJsonSchemaResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoDeleteOneJsonSchemaResponse message to deserialize.

        Returns:
            The deserialized MongoDB delete one JSON schema response dictionary.
        """
        return dtypes.MongoDeleteOneJsonSchemaResponse(
            success=proto.success,
            message=proto.message,
            status=proto.status,
            extra=dict(proto.extra),
        )

    @staticmethod
    def serialize_delete_import_name_request(
        request: dtypes.MongoDeleteImportNameRequest,
    ) -> mongo_pb2.MongoDeleteImportNameRequest:
        """Serialize a MongoDeleteImportNameRequest dictionary to Protocol Buffer format.

        Args:
            request: The MongoDB delete import name request dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoDeleteImportNameRequest message.
        """
        return mongo_pb2.MongoDeleteImportNameRequest(
            import_name=request["import_name"],
        )

    @staticmethod
    def deserialize_delete_import_name_request(
        proto: mongo_pb2.MongoDeleteImportNameRequest,
    ) -> dtypes.MongoDeleteImportNameRequest:
        """Deserialize a Protocol Buffer MongoDeleteImportNameRequest to dictionary format.

        Args:
            proto: The Protocol Buffer MongoDeleteImportNameRequest message to deserialize.

        Returns:
            The deserialized MongoDB delete import name request dictionary.
        """
        return dtypes.MongoDeleteImportNameRequest(
            import_name=proto.import_name,
        )

    @staticmethod
    def serialize_delete_import_name_response(
        response: dtypes.MongoDeleteImportNameResponse,
    ) -> mongo_pb2.MongoDeleteImportNameResponse:
        """Serialize a MongoDeleteImportNameResponse dictionary to Protocol Buffer format.

        Args:
            response: The MongoDB delete import name response dictionary to serialize.

        Returns:
            The serialized Protocol Buffer MongoDeleteImportNameResponse message.
        """
        return mongo_pb2.MongoDeleteImportNameResponse(
            success=response["success"],
            message=response["message"],
            status=response["status"],
            extra=response["extra"],
        )

    @staticmethod
    def deserialize_delete_import_name_response(
        proto: mongo_pb2.MongoDeleteImportNameResponse,
    ) -> dtypes.MongoDeleteImportNameResponse:
        """Deserialize a Protocol Buffer MongoDeleteImportNameResponse to dictionary format.

        Args:
            proto: The Protocol Buffer MongoDeleteImportNameResponse message to deserialize.

        Returns:
            The deserialized MongoDB delete import name response dictionary.
        """
        return dtypes.MongoDeleteImportNameResponse(
            success=proto.success,
            message=proto.message,
            status=proto.status,
            extra=dict(proto.extra),
        )
