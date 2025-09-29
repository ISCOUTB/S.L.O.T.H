"""gRPC request handlers for messaging service operations.

This module provides handler classes that process gRPC requests for the
messaging service. Handlers act as intermediaries between the gRPC server
layer and the business logic layer, managing serialization/deserialization
and request delegation.

Classes:
    MessagingHandler: Main handler class for all messaging-related gRPC requests

The handlers follow a consistent pattern:
1. Deserialize incoming gRPC protocol buffer requests
2. Delegate business logic to appropriate service classes
3. Serialize service responses back to protocol buffer format
4. Return formatted responses to the gRPC server layer

This separation ensures clean architecture with distinct responsibilities
for transport, serialization, and business logic.
"""

from proto_utils.generated.messaging import messaging_pb2
from proto_utils.messaging.messaging_serde import MessagingSerde

from src.services.params import MessagingParams


class MessagingHandler:
    """Handler class for messaging service gRPC requests.

    This class provides static methods to handle all messaging-related
    gRPC requests including parameter retrieval and routing key management.
    Each method follows the standard handler pattern of deserialization,
    service delegation, and response serialization.

    Methods:
        get_messaging_params: Handle requests for RabbitMQ connection parameters
        get_routing_key_schemas: Handle requests for schema routing key configuration
        get_routing_key_validations: Handle requests for validation routing key configuration

    Note:
        All methods are static as handlers are stateless and only provide
        request processing coordination between gRPC and service layers.
    """

    @staticmethod
    def get_messaging_params(
        request: messaging_pb2.GetMessagingParamsRequest,
    ) -> messaging_pb2.GetMessagingParamsResponse:
        """Handle GetMessagingParams gRPC requests.

        Processes requests for RabbitMQ connection parameters by deserializing
        the gRPC request, delegating to the parameters service, and serializing
        the response back to protocol buffer format.

        Args:
            request (messaging_pb2.GetMessagingParamsRequest): gRPC request
                containing any request parameters (currently unused)

        Returns:
            messaging_pb2.GetMessagingParamsResponse: Serialized response containing
                complete RabbitMQ connection configuration including host, port,
                credentials, exchange information, and queue definitions

        Raises:
            Exception: If parameter retrieval or serialization fails
        """
        deserialized_request = (
            MessagingSerde.deserialize_get_messaging_params_request(request)
        )
        service_response = MessagingParams.get_messaging_params(
            deserialized_request
        )
        return MessagingSerde.serialize_get_messaging_params_response(
            service_response
        )

    @staticmethod
    def get_routing_key_schemas(
        request: messaging_pb2.GetRoutingKeySchemasRequest,
    ) -> messaging_pb2.RoutingKey:
        """Handle GetRoutingKeySchemas gRPC requests.

        Processes requests for schema message routing key configuration by
        deserializing the request, determining the appropriate routing key
        based on request parameters, and returning the serialized response.

        Args:
            request (messaging_pb2.GetRoutingKeySchemasRequest): gRPC request
                containing routing key parameters (e.g., results flag)

        Returns:
            messaging_pb2.RoutingKey: Serialized response containing the
                appropriate routing key for schema messages

        Raises:
            Exception: If routing key retrieval or serialization fails
        """
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
        """Handle GetRoutingKeyValidations gRPC requests.

        Processes requests for validation message routing key configuration by
        deserializing the request, determining the appropriate routing key
        based on request parameters, and returning the serialized response.

        Args:
            request (messaging_pb2.GetRoutingKeyValidationsRequest): gRPC request
                containing routing key parameters (e.g., results flag)

        Returns:
            messaging_pb2.RoutingKey: Serialized response containing the
                appropriate routing key for validation messages

        Raises:
            Exception: If routing key retrieval or serialization fails
        """
        deserialized_request = (
            MessagingSerde.deserialize_get_routing_key_validations_request(
                request
            )
        )
        service_response = MessagingParams.get_routing_key_validations(
            deserialized_request
        )
        return MessagingSerde.serialize_routing_key(service_response)
