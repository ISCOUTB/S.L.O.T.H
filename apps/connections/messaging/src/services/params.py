"""Messaging parameters service implementation.

This module provides business logic for retrieving messaging configuration
parameters and routing keys. It serves as the core service layer that handles
the actual parameter retrieval and routing logic based on client requests.

Classes:
    MessagingParams: Service class for messaging parameter operations

The service layer is responsible for:
- Managing access to messaging configuration parameters
- Implementing routing key selection logic based on request parameters
- Providing clean, typed interfaces for parameter retrieval
- Ensuring data consistency and immutability through deep copying

Queue Index Mapping:
    Index 0: Schema messages queue (schemas.*)
    Index 1: Validation messages queue (validation.*)
    Index 2: Schema results queue (schemas.result.*)
    Index 3: Validation results queue (validation.result.*)
"""

from proto_utils.messaging import dtypes

from src.core.connection_params import messaging_params


class MessagingParams:
    """Service class for messaging parameter and routing key operations.

    This class provides static methods for retrieving messaging configuration
    parameters and determining appropriate routing keys based on client requests.
    All methods are stateless and operate on the global messaging configuration.

    Methods:
        get_messaging_params: Retrieve complete messaging configuration
        get_routing_key_schemas: Get routing key for schema messages
        get_routing_key_validations: Get routing key for validation messages

    Note:
        All methods return copies of configuration data to prevent
        accidental modification of the global configuration state.
    """

    @staticmethod
    def get_messaging_params(
        _: dtypes.GetMessagingParamsRequest = None,
    ) -> dtypes.GetMessagingParamsResponse:
        """Retrieve complete messaging configuration parameters.

        Returns a copy of the complete messaging configuration including
        RabbitMQ connection parameters, exchange information, and queue
        definitions. This method provides all necessary information for
        clients to establish connections and interact with the message broker.

        Args:
            _ (dtypes.GetMessagingParamsRequest, optional): Request parameters
                (currently unused but maintained for API consistency)

        Returns:
            dtypes.GetMessagingParamsResponse: Complete messaging configuration
                including connection details, exchange settings, and queue information

        Note:
            Returns a deep copy to prevent modification of global configuration.
        """
        return messaging_params.copy()

    @staticmethod
    def get_routing_key_schemas(
        message: dtypes.GetRoutingKeySchemasRequest,
    ) -> dtypes.RoutingKey:
        """Determine appropriate routing key for schema messages.

        Selects the correct routing key for schema messages based on whether
        the request is for regular schema operations or schema results.
        This allows clients to publish to or consume from the appropriate queues.

        Args:
            message (dtypes.GetRoutingKeySchemasRequest): Request containing
                routing key selection parameters, particularly the 'results' flag

        Returns:
            dtypes.RoutingKey: Routing key configuration for schema messages
                - If results=True: Returns schema results routing key (queue index 2)
                - If results=False: Returns standard schema routing key (queue index 0)

        Queue Selection Logic:
            - Standard schemas: Index 0 (schemas.*)
            - Schema results: Index 2 (schemas.result.*)
        """
        if message["results"]:
            return dtypes.RoutingKey(
                routing_key=messaging_params["exchange"]["queues"][2][
                    "routing_key"
                ],
            )
        return dtypes.RoutingKey(
            routing_key=messaging_params["exchange"]["queues"][0][
                "routing_key"
            ],
        )

    @staticmethod
    def get_routing_key_validations(
        message: dtypes.GetRoutingKeyValidationsRequest,
    ) -> dtypes.RoutingKey:
        """Determine appropriate routing key for validation messages.

        Selects the correct routing key for validation messages based on whether
        the request is for regular validation operations or validation results.
        This allows clients to publish to or consume from the appropriate queues.

        Args:
            message (dtypes.GetRoutingKeyValidationsRequest): Request containing
                routing key selection parameters, particularly the 'results' flag

        Returns:
            dtypes.RoutingKey: Routing key configuration for validation messages
                - If results=True: Returns validation results routing key (queue index 3)
                - If results=False: Returns standard validation routing key (queue index 1)

        Queue Selection Logic:
            - Standard validations: Index 1 (validation.*)
            - Validation results: Index 3 (validation.result.*)
        """
        if message["results"]:
            return dtypes.RoutingKey(
                routing_key=messaging_params["exchange"]["queues"][3][
                    "routing_key"
                ],
            )
        return dtypes.RoutingKey(
            routing_key=messaging_params["exchange"]["queues"][1][
                "routing_key"
            ],
        )
