"""Unit tests for messaging parameter services.

This module contains unit tests for the MessagingParams service class,
which handles retrieval and configuration of messaging-related parameters
including connection settings and routing key configurations.

Test Functions:
    test_get_messaging_params: Validates messaging connection parameter retrieval
    test_get_routing_key_schemas: Tests schema routing key configuration
    test_get_routing_key_validations: Tests validation routing key configuration

The tests verify that parameter services correctly return expected values
from the configured messaging parameters and handle different request types
appropriately for both result and non-result routing scenarios.

Dependencies:
    - proto_utils.messaging.dtypes: Type definitions for messaging requests
    - src.core.connection_params: Core messaging parameter configuration
    - src.services.params: MessagingParams service implementation
"""

from proto_utils.messaging import dtypes

from src.core.connection_params import messaging_params
from src.services.params import MessagingParams


def test_get_messaging_params() -> None:
    """Test retrieval of messaging connection parameters.

    Verifies that the MessagingParams service correctly returns
    the configured messaging parameters without modification.

    Asserts:
        The returned parameters match the expected messaging_params configuration
    """
    response = MessagingParams.get_messaging_params()
    assert response == messaging_params


def test_get_routing_key_schemas() -> None:
    """Test retrieval of schema routing keys for different request types.

    Verifies that routing key retrieval works correctly for both:
    1. Non-result requests (results=False): Returns standard schema routing key
    2. Result requests (results=True): Returns schema results routing key

    Tests the correct mapping between request parameters and queue configurations
    based on the messaging_params exchange queue definitions.

    Asserts:
        - Non-result requests return queue[0] routing key (standard schemas)
        - Result requests return queue[2] routing key (schema results)
    """
    request = dtypes.GetRoutingKeySchemasRequest(results=False)
    response = MessagingParams.get_routing_key_schemas(request)
    assert response == dtypes.RoutingKey(
        routing_key=messaging_params["exchange"]["queues"][0]["routing_key"],
    )

    request = dtypes.GetRoutingKeySchemasRequest(results=True)
    response = MessagingParams.get_routing_key_schemas(request)
    assert response == dtypes.RoutingKey(
        routing_key=messaging_params["exchange"]["queues"][2]["routing_key"],
    )


def test_get_routing_key_validations() -> None:
    """Test retrieval of validation routing keys for different request types.

    Verifies that validation routing key retrieval works correctly for both:
    1. Non-result requests (results=False): Returns standard validation routing key
    2. Result requests (results=True): Returns validation results routing key

    Tests the correct mapping between request parameters and queue configurations
    based on the messaging_params exchange queue definitions.

    Asserts:
        - Non-result requests return queue[1] routing key (standard validations)
        - Result requests return queue[3] routing key (validation results)
    """
    request = dtypes.GetRoutingKeyValidationsRequest(results=False)
    response = MessagingParams.get_routing_key_validations(request)
    assert response == dtypes.RoutingKey(
        routing_key=messaging_params["exchange"]["queues"][1]["routing_key"],
    )

    request = dtypes.GetRoutingKeyValidationsRequest(results=True)
    response = MessagingParams.get_routing_key_validations(request)
    assert response == dtypes.RoutingKey(
        routing_key=messaging_params["exchange"]["queues"][3]["routing_key"],
    )
