from proto_utils.messaging import dtypes
from proto_utils.generated.messaging import dtypes_pb2
from proto_utils.generated.messaging import messaging_pb2
from proto_utils.messaging.schemas_serde import SchemasSerde
from proto_utils.messaging.validation_serde import ValidationSerde
from proto_utils.database.utils_serde import DatabaseUtilsSerde


class MessagingSerde:
    @staticmethod
    def serialize_queue_info(queue: dtypes.QueueInfo) -> dtypes_pb2.QueueInfo:
        return dtypes_pb2.QueueInfo(
            queue=queue["queue"],
            durable=queue["durable"],
            routing_key=queue["routing_key"],
        )

    @staticmethod
    def deserialize_queue_info(proto: dtypes_pb2.QueueInfo) -> dtypes.QueueInfo:
        return dtypes.QueueInfo(
            queue=proto.queue,
            routing_key=proto.routing_key,
            durable=proto.durable,
        )

    @staticmethod
    def serialize_exchange_info(
        exchange: dtypes.ExchangeInfo,
    ) -> dtypes_pb2.ExchangeInfo:
        return dtypes_pb2.ExchangeInfo(
            exchange=exchange["exchange"],
            type=exchange["type"],
            durable=exchange["durable"],
            queues=list(map(MessagingSerde.serialize_queue_info, exchange["queues"])),
        )

    @staticmethod
    def deserialize_exchange_info(
        proto: dtypes_pb2.ExchangeInfo,
    ) -> dtypes.ExchangeInfo:
        return dtypes.ExchangeInfo(
            exchange=proto.exchange,
            type=proto.type,
            durable=proto.durable,
            queues=list(map(MessagingSerde.deserialize_queue_info, proto.queues)),
        )

    @staticmethod
    def serialize_get_messaging_params_request(
        message: dtypes.GetMessagingParamsRequest,
    ) -> messaging_pb2.GetMessagingParamsRequest:
        return messaging_pb2.GetMessagingParamsRequest()

    @staticmethod
    def deserialize_get_messaging_params_request(
        proto: messaging_pb2.GetMessagingParamsRequest,
    ) -> dtypes.GetMessagingParamsRequest:
        return dtypes.GetMessagingParamsRequest()

    @staticmethod
    def serialize_get_messaging_params_response(
        message: dtypes.GetMessagingParamsResponse,
    ) -> messaging_pb2.GetMessagingParamsResponse:
        return messaging_pb2.GetMessagingParamsResponse(
            host=message["host"],
            port=message["port"],
            username=message["username"],
            password=message["password"],
            virtual_host=message["virtual_host"],
            exchange=MessagingSerde.serialize_exchange_info(message["exchange"]),
        )

    def deserialize_get_messaging_params_response(
        proto: messaging_pb2.GetMessagingParamsResponse,
    ) -> dtypes.GetMessagingParamsResponse:
        return dtypes.GetMessagingParamsResponse(
            host=proto.host,
            port=proto.port,
            username=proto.username,
            password=proto.password,
            virtual_host=proto.virtual_host,
            exchange=MessagingSerde.deserialize_exchange_info(proto.exchange),
        )

    @staticmethod
    def serialize_get_routing_key_schemas_request(
        message: dtypes.GetRoutingKeySchemasRequest,
    ) -> messaging_pb2.GetRoutingKeySchemasRequest:
        return messaging_pb2.GetRoutingKeySchemasRequest(results=message["results"])

    @staticmethod
    def deserialize_get_routing_key_schemas_request(
        proto: messaging_pb2.GetRoutingKeySchemasRequest,
    ) -> dtypes.GetRoutingKeySchemasRequest:
        return dtypes.GetRoutingKeySchemasRequest(results=proto.results)

    @staticmethod
    def serialize_routing_key(
        message: dtypes.RoutingKey,
    ) -> messaging_pb2.RoutingKey:
        return messaging_pb2.RoutingKey(routing_key=message["routing_key"])

    @staticmethod
    def deserialize_routing_key(
        proto: messaging_pb2.RoutingKey,
    ) -> dtypes.RoutingKey:
        return dtypes.RoutingKey(routing_key=proto.routing_key)

    @staticmethod
    def serialize_get_routing_key_validations_request(
        message: dtypes.GetRoutingKeyValidationsRequest,
    ) -> messaging_pb2.GetRoutingKeyValidationsRequest:
        return messaging_pb2.GetRoutingKeyValidationsRequest(results=message["results"])

    @staticmethod
    def deserialize_get_routing_key_validations_request(
        proto: messaging_pb2.GetRoutingKeyValidationsRequest,
    ) -> dtypes.GetRoutingKeyValidationsRequest:
        return dtypes.GetRoutingKeyValidationsRequest(results=proto.results)

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
