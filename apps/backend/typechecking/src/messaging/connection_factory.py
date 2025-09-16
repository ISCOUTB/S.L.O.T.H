"""RabbitMQ Connection Factory Module.

This module provides a thread-safe RabbitMQ connection factory that manages
connections and channels for each thread, ensuring proper resource management
and thread isolation. The factory pattern allows for efficient resource
sharing while maintaining thread safety.

The factory manages per-thread connections and channels, automatically
creating new ones when needed and providing proper cleanup mechanisms.

Example:
    Using the connection factory:

    >>> from app.messaging.connection_factory import RabbitMQConnectionFactory
    >>>
    >>> # Get a thread-specific channel with context manager
    >>> with RabbitMQConnectionFactory.get_channel() as channel:
    ...     # Use channel for messaging operations
    ...     channel.basic_publish(exchange='test', routing_key='key', body='message')
    >>>
    >>> # Or get connection/channel directly
    >>> connection = RabbitMQConnectionFactory.get_thread_connection()
    >>> channel = RabbitMQConnectionFactory.get_thread_channel()
"""

import pika
from pika.adapters.blocking_connection import BlockingChannel

import logging
import threading
from typing import Dict, Generator
from contextlib import contextmanager
from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            virtual_host=settings.RABBITMQ_VHOST,
            credentials=pika.PlainCredentials(
                username=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
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
            logger.info("New RabbitMQ connection created")
            return connection
        except Exception as e:
            logger.error(f"Failed to create RabbitMQ connection: {e}")
            raise

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
                exchange="typechecking.exchange",
                exchange_type="topic",
                durable=True,
            )

            # Declare queues
            queues = [
                "typechecking.validation.queue",
                "typechecking.schema.queue",
                "typechecking.results.schema.queue",
                "typechecking.results.validation.queue",
            ]

            for queue in queues:
                channel.queue_declare(queue=queue, durable=True)

            # Bind queues to exchange
            channel.queue_bind(
                exchange="typechecking.exchange",
                queue="typechecking.validation.queue",
                routing_key="validation.*",
            )

            channel.queue_bind(
                exchange="typechecking.exchange",
                queue="typechecking.schema.queue",
                routing_key="schema.*",
            )

            channel.queue_bind(
                exchange="typechecking.exchange",
                queue="typechecking.results.schema.queue",
                routing_key="results.schema",
            )

            channel.queue_bind(
                exchange="typechecking.exchange",
                queue="typechecking.results.validation.queue",
                routing_key="results.validation",
            )

            logger.info("RabbitMQ infrastructure setup completed")
        except Exception as e:
            logger.error(f"Failed to setup RabbitMQ infrastructure: {e}")
            raise

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
                logger.info("Thread channel closed")

            # Close connection
            if (
                thread_id in cls._connections
                and cls._connections[thread_id].is_open
            ):
                cls._connections[thread_id].close()
                del cls._connections[thread_id]
                logger.info("Thread connection closed")

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
            logger.error(f"Error in channel context: {e}")
            raise
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
