from proto_utils.messaging import dtypes

from src.core.connection_params import messaging_params


class MessagingParams:
    @staticmethod
    def get_messaging_params(
        _: dtypes.GetMessagingParamsRequest = None,
    ) -> dtypes.GetMessagingParamsResponse:
        return messaging_params.copy()

    @staticmethod
    def get_routing_key_schemas(
        message: dtypes.GetRoutingKeySchemasRequest,
    ) -> dtypes.RoutingKey:
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
