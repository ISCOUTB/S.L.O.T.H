import pika
import pytest
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.messaging.publishers import Publisher
from messaging_utils.schemas.connection import ConnectionParams

from src.core.connection_params import messaging_params

RabbitMQConnectionFactory.configure(messaging_params)


def purge_queue(queue_name: str) -> None:
    """Purge all messages from a queue."""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=messaging_params["host"],
                port=messaging_params["port"],
                virtual_host=messaging_params["virtual_host"],
                credentials=pika.PlainCredentials(
                    messaging_params["username"], messaging_params["password"]
                ),
            )
        )
        channel = connection.channel()
        channel.queue_purge(queue_name)
        connection.close()
    except Exception:
        pass  # Ignore errors if queue doesn't exist or other connection issues


@pytest.fixture(scope="function")
def publisher() -> Publisher:
    """Create a new publisher instance for each test to avoid connection issues."""
    return Publisher(
        params=ConnectionParams(
            host=messaging_params["host"],
            port=messaging_params["port"],
            virtual_host=messaging_params["virtual_host"],
            username=messaging_params["username"],
            password=messaging_params["password"],
        ),
        exchange_info=messaging_params["exchange"],
    )


@pytest.fixture(autouse=True)
def clean_queues() -> None:
    """Clean all test queues before each test."""
    from src.core.config import settings

    purge_queue(settings.RABBITMQ_QUEUE_VALIDATIONS)
    purge_queue(settings.RABBITMQ_QUEUE_SCHEMAS)
