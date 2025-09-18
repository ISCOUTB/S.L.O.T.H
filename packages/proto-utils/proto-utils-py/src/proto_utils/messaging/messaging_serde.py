from proto_utils.messaging import dtypes
from proto_utils.generated.messaging import messaging_pb2
from proto_utils.messaging.schemas_serde import SchemasSerde
from proto_utils.messaging.validation_serde import ValidationSerde
from proto_utils.database.utils_serde import DatabaseUtilsSerde


class MessagingSerde:
    @staticmethod
    def serialize_schema_message_request(
        message: dtypes.SchemaMessageRequest,
    ) -> messaging_pb2.SchemaMessageRequest:
        return messaging_pb2.SchemaMessageRequest()

    @staticmethod
    def deserialize_schema_message_request(
        proto: messaging_pb2.SchemaMessageRequest,
    ) -> dtypes.SchemaMessageRequest:
        return dtypes.SchemaMessageRequest()

    @staticmethod
    def serialize_schema_message_response(
        message: dtypes.SchemaMessageResponse,
    ) -> messaging_pb2.SchemaMessageResponse:
        return messaging_pb2.SchemaMessageResponse(
            id=message["id"],
            schema=DatabaseUtilsSerde.serialize_jsonschema(message["schema"]),
            import_name=message["import_name"],
            raw=message["raw"],
            task=SchemasSerde.serialize_schemas_tasks(message["tasks"]),
            date=message["date"],
            extra=message.get("extra", {}),
        )

    @staticmethod
    def deserialize_schema_message_response(
        proto: messaging_pb2.SchemaMessageResponse,
    ) -> dtypes.SchemaMessageResponse:
        return dtypes.SchemaMessageResponse(
            id=proto.id,
            schema=DatabaseUtilsSerde.deserialize_jsonschema(proto.schema),
            import_name=proto.import_name,
            raw=proto.raw,
            tasks=SchemasSerde.deserialize_schemas_tasks(proto.task),
            date=proto.date,
            extra=dict(proto.extra),
        )

    @staticmethod
    def serialize_validation_message_request(
        message: dtypes.ValidationMessageRequest,
    ) -> messaging_pb2.ValidationMessageRequest:
        return messaging_pb2.ValidationMessageRequest()

    @staticmethod
    def deserialize_validation_message_request(
        proto: messaging_pb2.ValidationMessageRequest,
    ) -> dtypes.ValidationMessageRequest:
        return dtypes.ValidationMessageRequest()

    @staticmethod
    def serialize_validation_message_response(
        message: dtypes.ValidationMessageResponse,
    ) -> messaging_pb2.ValidationMessageResponse:
        return messaging_pb2.ValidationMessageResponse(
            id=message["id"],
            task=ValidationSerde.serialize_validation_tasks(message["task"]),
            file_data=message["file_data"],
            import_name=message["import_name"],
            metadata=ValidationSerde.serialize_metadata(message["metadata"]),
            date=message["date"],
            extra=message.get("extra", {}),
        )

    @staticmethod
    def deserialize_validation_message_response(
        proto: messaging_pb2.ValidationMessageResponse,
    ) -> dtypes.ValidationMessageResponse:
        return dtypes.ValidationMessageResponse(
            id=proto.id,
            task=ValidationSerde.deserialize_validation_tasks(proto.task),
            file_data=proto.file_data,
            import_name=proto.import_name,
            metadata=ValidationSerde.deserialize_metadata(proto.metadata),
            date=proto.date,
            extra=dict(proto.extra),
        )
