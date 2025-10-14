"""RabbitMQ Connection Factory Module.

This module provides a thread-safe RabbitMQ connection factory that manages
connections and channels for each thread, ensuring proper resource management
and thread isolation. The factory pattern allows for efficient resource
sharing while maintaining thread safety.

The factory manages per-thread connections and channels, automatically
creating new ones when needed and providing proper cleanup mechanisms.
"""

import threading
from contextlib import contextmanager
from typing import Dict, Generator, Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel
from proto_utils.messaging.dtypes import (
    ExchangeInfo,
    GetMessagingParamsResponse,
)

from messaging_utils.core.connection_params import messaging_params
from messaging_utils.schemas.connection import ConnectionParams


class RabbitMQConnectionFactory:
    """Factory to create RabbitMQ connections with proper thread isolation.

    This factory class manages RabbitMQ connections and channels on a per-thread
    basis, ensuring thread safety and proper resource management. Each thread
    gets its own connection and channel, preventing conflicts in multi-threaded
    environments.

    The factory uses a thread-safe design with RLock to manage concurrent
    access to the connection and channel dictionaries.

    Attributes:
        _connections: Dictionary mapping thread IDs to their connections.
        _channels: Dictionary mapping thread IDs to their channels.
        _lock: Reentrant lock for thread-safe operations.
    """

    _connections: Dict[int, pika.BlockingConnection] = {}
    _channels: Dict[int, BlockingChannel] = {}
    _lock = threading.RLock()
    _params: ConnectionParams = ConnectionParams()
    _exchange_info: ExchangeInfo = ExchangeInfo()

    @classmethod
    def configure(
        cls, connection_params: Optional[GetMessagingParamsResponse] = None
    ) -> None:
        """Configure the connection factory with connection parameters.

        This method sets the connection parameters for the factory.
        It should be called once during application initialization.

        Args:
            connection_params: ConnectionParams object containing
                RabbitMQ connection details.
        """
        if connection_params is None:
            connection_params = messaging_params

        connection_params = connection_params.copy()
        cls._exchange_info = connection_params["exchange"].copy()

        connection_params.pop("exchange", None)
        cls._params = connection_params

    @classmethod
    def get_exchange_info(cls) -> ExchangeInfo:
        """Get the configured exchange information.

        Returns:
            ExchangeInfo: The exchange and queue configuration details.
        """
        return cls._exchange_info.copy()

    @classmethod
    def get_connection_params(cls) -> pika.ConnectionParameters:
        """Get standardized connection parameters.

        Creates connection parameters using application settings,
        providing a centralized configuration point for all connections.

        Returns:
            pika.ConnectionParameters: Configured connection parameters
                with host, port, credentials, and timeout settings.
        """
        return pika.ConnectionParameters(
            host=cls._params["host"],
            port=cls._params["port"],
            virtual_host=cls._params["virtual_host"],
            credentials=pika.PlainCredentials(
                username=cls._params["username"],
                password=cls._params["password"],
            ),
            heartbeat=600,
            blocked_connection_timeout=300,
        )

    @classmethod
    def create_connection(cls) -> pika.BlockingConnection:
        """Create a new RabbitMQ connection.

        Creates a new blocking connection to RabbitMQ using the standardized
        connection parameters. This method is used internally by the factory
        to create connections for each thread.

        Returns:
            pika.BlockingConnection: New RabbitMQ blocking connection.

        Raises:
            Exception: If connection creation fails due to network issues,
                authentication problems, or other RabbitMQ errors.
        """
        try:
            connection_params = cls.get_connection_params()
            connection = pika.BlockingConnection(connection_params)
            return connection
        except Exception as e:
            raise e

    @classmethod
    def get_thread_connection(cls) -> pika.BlockingConnection:
        """Get or create a connection for the current thread.

        Returns an existing connection for the current thread, or creates
        a new one if none exists or if the existing connection is closed.
        This ensures each thread has its own isolated connection.

        Returns:
            pika.BlockingConnection: Thread-specific RabbitMQ connection.

        Raises:
            Exception: If connection creation fails.
        """
        thread_id = threading.get_ident()

        with cls._lock:
            if (
                thread_id not in cls._connections
                or cls._connections[thread_id].is_closed
            ):
                cls._connections[thread_id] = cls.create_connection()

            return cls._connections[thread_id]

    @classmethod
    def get_thread_channel(cls) -> BlockingChannel:
        """Get or create a channel for the current thread.

        Returns an existing channel for the current thread, or creates
        a new one if none exists or if the existing channel is closed.
        Channels are created from the thread's connection.

        Returns:
            BlockingChannel: Thread-specific RabbitMQ channel ready for
                messaging operations.

        Raises:
            Exception: If channel creation fails or connection issues occur.
        """
        thread_id = threading.get_ident()
        with cls._lock:
            connection = cls.get_thread_connection()
            if (
                thread_id not in cls._channels
                or cls._channels[thread_id].is_closed
            ):
                cls._channels[thread_id] = connection.channel()

            return cls._channels[thread_id]

    @classmethod
    def setup_infrastructure(cls, channel: pika.channel.Channel) -> None:
        """Set up exchanges and queues for messaging.

        Declares the necessary messaging infrastructure including exchanges,
        queues, and bindings required for the typechecking application.
        This method is idempotent and safe to call multiple times.

        Args:
            channel: RabbitMQ channel to use for infrastructure setup.

        Infrastructure created:
            - Exchange: typechecking.exchange (topic, durable)
            - Queues: validation, schema, and results queues (all durable)
            - Bindings: Appropriate routing key bindings for message routing

        Raises:
            Exception: If exchange/queue declaration or binding fails.
        """
        try:
            channel.exchange_declare(
                exchange=cls._exchange_info["exchange"],
                exchange_type=cls._exchange_info["type"],
                durable=cls._exchange_info["durable"],
            )

            # Declare queues
            for queue in cls._exchange_info["queues"]:
                channel.queue_declare(
                    queue=queue["queue"], durable=queue["durable"]
                )

                # Bind queue to exchange with routing key
                channel.queue_bind(
                    exchange=cls._exchange_info["exchange"],
                    queue=queue["queue"],
                    routing_key=queue["routing_key"],
                )
        except Exception as e:
            raise e

    @classmethod
    def close_thread_connections(cls) -> None:
        """Close connections for the current thread.

        Safely closes and removes the channel and connection associated
        with the current thread. This should be called when a thread
        is finished with RabbitMQ operations to prevent resource leaks.

        The method handles cases where connections/channels are already
        closed and logs the cleanup operations.
        """
        thread_id = threading.get_ident()

        with cls._lock:
            # Close channel
            if thread_id in cls._channels and cls._channels[thread_id].is_open:
                cls._channels[thread_id].close()
                del cls._channels[thread_id]

            # Close connection
            if (
                thread_id in cls._connections
                and cls._connections[thread_id].is_open
            ):
                cls._connections[thread_id].close()
                del cls._connections[thread_id]

    @classmethod
    @contextmanager
    def get_channel(cls) -> Generator[BlockingChannel, None, None]:
        """Context manager for getting a channel.

        Provides a context manager that yields a properly configured
        RabbitMQ channel with infrastructure setup. The channel remains
        open after the context exits to allow for worker thread reuse.

        Yields:
            BlockingChannel: Configured RabbitMQ channel with messaging
                infrastructure already set up.

        Raises:
            Exception: If channel acquisition or infrastructure setup fails.

        Example:
            >>> with RabbitMQConnectionFactory.get_channel() as channel:
            ...     channel.basic_publish(
            ...         exchange='typechecking.exchange',
            ...         routing_key='validation.request',
            ...         body='message'
            ...     )
        """
        channel = None
        try:
            channel = cls.get_thread_channel()
            cls.setup_infrastructure(channel)
            yield channel
        except Exception as e:
            raise e
        finally:
            # Don't close here - let workers manage their own lifecycle
            pass


# Convenience functions for backward compatibility
def get_rabbitmq_connection() -> pika.BlockingConnection:
    """Get a RabbitMQ connection for the current thread.

    Convenience function that provides backward compatibility and
    a simpler interface for getting thread-specific connections.

    Returns:
        pika.BlockingConnection: Thread-specific RabbitMQ connection.

    Raises:
        Exception: If connection creation fails.
    """
    return RabbitMQConnectionFactory.get_thread_connection()


def get_rabbitmq_channel() -> BlockingChannel:
    """Get a RabbitMQ channel for the current thread.

    Convenience function that provides backward compatibility and
    a simpler interface for getting thread-specific channels.

    Returns:
        pika.adapters.blocking_connection.BlockingChannel:
        Thread-specific RabbitMQ channel.

    Raises:
        Exception: If channel creation fails.
    """
    return RabbitMQConnectionFactory.get_thread_channel()
