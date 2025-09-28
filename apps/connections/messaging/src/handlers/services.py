from proto_utils.generated.messaging import messaging_pb2
from proto_utils.messaging.messaging_serde import MessagingSerde

from src.services.params import MessagingParams


class MessagingHandler:
    @staticmethod
    def get_messaging_params(
        request: messaging_pb2.GetMessagingParamsRequest,
    ) -> messaging_pb2.GetMessagingParamsResponse:
        deserialized_request = (
            MessagingSerde.deserialize_get_messaging_params_request(request)
        )
        service_response = MessagingParams.get_messaging_params(
            deserialized_request
        )
        return MessagingSerde.serialize_get_messaging_params_response(service_response)

    @staticmethod
    def get_routing_key_schemas(
        request: messaging_pb2.GetRoutingKeySchemasRequest,
    ) -> messaging_pb2.RoutingKey:
        deserialized_request = (
            MessagingSerde.deserialize_get_routing_key_schemas_request(request)
        )
        service_response = MessagingParams.get_routing_key_schemas(
            deserialized_request
        )
        return MessagingSerde.serialize_routing_key(service_response)

    @staticmethod
    def get_routing_key_validations(
        request: messaging_pb2.GetRoutingKeyValidationsRequest,
    ) -> messaging_pb2.RoutingKey:
        deserialized_request = (
            MessagingSerde.deserialize_get_routing_key_validations_request(
                request
            )
        )
        service_response = MessagingParams.get_routing_key_validations(
            deserialized_request
        )
        return MessagingSerde.serialize_routing_key(service_response)
