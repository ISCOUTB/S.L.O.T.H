"""RabbitMQ connection parameters configuration module.

This module constructs a complete messaging parameters response object that
contains all necessary information for clients to connect to and interact
with the RabbitMQ message broker. It transforms application settings into
the standardized protocol buffer format used by gRPC clients.

Constants:
    messaging_params: Complete messaging configuration including connection
                     details, exchange information, and queue definitions

The messaging_params object serves as the authoritative source for all
RabbitMQ configuration distributed to clients via the GetMessagingParams
gRPC endpoint.
"""

from messaging_utils.core.config import settings
from messaging_utils.schemas.connection import (
    AllConnectionParams,
    ExchangeInfo,
    QueueInfo,
)

# Complete messaging parameters configuration for client distribution
messaging_params = AllConnectionParams(
    host=settings.RABBITMQ_HOST,
    port=settings.RABBITMQ_PORT,
    username=settings.RABBITMQ_USER,
    password=settings.RABBITMQ_PASSWORD,
    virtual_host=settings.RABBITMQ_VHOST,
    exchange=ExchangeInfo(
        exchange=settings.RABBITMQ_EXCHANGE,
        durable=True,
        type=settings.RABBITMQ_EXCHANGE_TYPE,
        queues=[
            # Schema message queue configuration
            QueueInfo(
                queue=settings.RABBITMQ_QUEUE_SCHEMAS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
                durable=True,
            ),
            # Validation message queue configuration
            QueueInfo(
                queue=settings.RABBITMQ_QUEUE_VALIDATIONS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
                durable=True,
            ),
            # Schema results queue configuration
            QueueInfo(
                queue=settings.RABBITMQ_QUEUE_RESULTS_SCHEMAS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS,
                durable=True,
            ),
            # Validation results queue configuration
            QueueInfo(
                queue=settings.RABBITMQ_QUEUE_RESULTS_VALIDATIONS,
                routing_key=settings.RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS,
                durable=True,
            ),
        ],
    ),
)
