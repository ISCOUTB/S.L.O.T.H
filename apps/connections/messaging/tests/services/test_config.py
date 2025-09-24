from proto_utils.messaging import dtypes

from src.core.connection_params import messaging_params
from src.services.config import MessagingParams


def test_get_messaging_params() -> None:
    response = MessagingParams.get_messaging_params()
    assert response == messaging_params


def test_get_routing_key_schemas() -> None:
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
