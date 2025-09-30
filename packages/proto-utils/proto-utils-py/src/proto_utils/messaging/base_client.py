from typing import Generator

import grpc
from proto_utils.messaging import dtypes
from proto_utils.messaging.messaging_serde import MessagingSerde
from proto_utils.generated.messaging.messaging_pb2_grpc import MessagingServiceStub


class MessagingClient:
    def __init__(self, channel: str) -> None:
        self.channel = grpc.insecure_channel(channel)
        self.stub = MessagingServiceStub(self.channel)

    def get_messaging_params(
        self, request: dtypes.GetMessagingParamsRequest = None
    ) -> dtypes.GetMessagingParamsResponse:
        if request is None:
            request = dtypes.GetMessagingParamsRequest()
        request_proto = MessagingSerde.serialize_get_messaging_params_request(request)
        response = self.stub.GetMessagingParams(request_proto)
        return MessagingSerde.deserialize_get_messaging_params_response(response)

    def get_routing_key_schemas(
        self, request: dtypes.GetRoutingKeySchemasRequest
    ) -> dtypes.RoutingKey:
        request_proto = MessagingSerde.serialize_get_routing_key_schemas_request(
            request
        )
        response = self.stub.GetRoutingKeySchemas(request_proto)
        return MessagingSerde.deserialize_routing_key(response)

    def get_routing_key_validations(
        self, request: dtypes.GetRoutingKeyValidationsRequest
    ) -> dtypes.RoutingKey:
        request_proto = MessagingSerde.serialize_get_routing_key_validations_request(
            request
        )
        response = self.stub.GetRoutingKeyValidations(request_proto)
        return MessagingSerde.deserialize_routing_key(response)

    def stream_schema_messages(
        self, request: dtypes.SchemaMessageRequest
    ) -> Generator[dtypes.SchemaMessageResponse, None, None]:
        request_proto = MessagingSerde.serialize_schema_message_request(request)
        responses = self.stub.StreamSchemaMessages(request_proto)
        for response in responses:
            yield MessagingSerde.deserialize_schema_message_response(response)

    def stream_validation_messages(
        self, request: dtypes.ValidationMessageRequest
    ) -> Generator[dtypes.ValidationMessageResponse, None, None]:
        request_proto = MessagingSerde.serialize_validation_message_request(request)
        responses = self.stub.StreamValidationMessages(request_proto)
        for response in responses:
            yield MessagingSerde.deserialize_validation_message_response(response)

    def close(self) -> None:
        self.channel.close()
