from proto_utils.messaging import dtypes

from src.core.config import settings

messaging_params: dtypes.GetMessagingParamsResponse = dtypes.GetMessagingParamsResponse(
    host=settings.RABBITMQ_HOST,
    port=settings.RABBITMQ_PORT,
    username=settings.RABBITMQ_USER,
    password=settings.RABBITMQ_PASSWORD,
    virtual_host=settings.RABBITMQ_VHOST,
    exchange=dtypes.ExchangeInfo(
        exchange=settings.RABBITMQ_EXCHANGE,
        durable=True,
        type=settings.RABBITMQ_EXCHANGE_TYPE,
        queues=[
            dtypes.QueueInfo(
                name=settings.RABBITMQ_QUEUE_SCHEMAS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
                durable=True,
            ),
            dtypes.QueueInfo(
                name=settings.RABBITMQ_QUEUE_VALIDATIONS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
                durable=True,
            ),
            dtypes.QueueInfo(
                name=settings.RABBITMQ_QUEUE_RESULTS_SCHEMAS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS,
                durable=True,
            ),
            dtypes.QueueInfo(
                name=settings.RABBITMQ_QUEUE_RESULTS_VALIDATIONS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS,
                durable=True,
            ),
        ],
    ),
)
