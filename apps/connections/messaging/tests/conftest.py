"""Pytest configuration and shared fixtures for messaging tests.

This module provides shared test configuration, fixtures, and utilities
for the messaging service test suite. It includes setup for RabbitMQ
connections, test data cleanup, and publisher instances.

Functions:
    purge_queue: Utility function to clean RabbitMQ queues between tests

Fixtures:
    publisher: Creates Publisher instance for message publishing in tests
    clean_queues: Automatically cleans test queues before each test execution

Configuration:
    - Sets up RabbitMQ connection factory with test parameters
    - Provides isolated publisher instances for each test
    - Ensures clean test environment by purging queues

Notes:
    - Uses function scope for publisher fixture to avoid connection conflicts
    - Automatically purges validation and schema queues before each test
    - Handles RabbitMQ connection errors gracefully during cleanup
"""

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
    """Purge all messages from a specified RabbitMQ queue.

    Creates a temporary connection to RabbitMQ and purges all messages
    from the specified queue. Used for test cleanup to ensure isolated
    test execution environments.

    Args:
        queue_name (str): Name of the queue to purge

    Notes:
        - Silently ignores connection errors and missing queues
        - Uses blocking connection for synchronous queue operations
        - Automatically closes connection after purge operation
    """
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
    """Create a new Publisher instance for each test function.

    Provides a fresh Publisher instance with configured RabbitMQ connection
    parameters for each test. Uses function scope to avoid connection conflicts
    and ensure test isolation.

    Returns:
        Publisher: Configured publisher instance with connection parameters
            and exchange information from messaging_params

    Notes:
        - Creates new instance per test to avoid connection state conflicts
        - Uses messaging_params configuration for consistent test environment
        - Includes both connection parameters and exchange configuration
    """
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
    """Automatically clean all test queues before each test execution.

    This fixture runs automatically before each test to ensure a clean
    message queue environment. Purges both validation and schema queues
    to prevent test interference from previous test runs.

    Queues Cleaned:
        - RABBITMQ_QUEUE_VALIDATIONS: Validation message queue
        - RABBITMQ_QUEUE_SCHEMAS: Schema message queue

    Notes:
        - Runs automatically (autouse=True) before every test
        - Uses settings from configuration for queue names
        - Silently handles queue purge errors during cleanup
    """
    from src.core.config import settings

    purge_queue(settings.RABBITMQ_QUEUE_VALIDATIONS)
    purge_queue(settings.RABBITMQ_QUEUE_SCHEMAS)
