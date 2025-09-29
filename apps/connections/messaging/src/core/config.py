"""Configuration module for the messaging gRPC server.

This module provides centralized configuration management using Pydantic settings
for the messaging service. It handles environment variable loading, validation,
and computed fields for connection strings and URIs.

Classes:
    Settings: Main configuration class with RabbitMQ and gRPC server settings

Constants:
    settings: Global settings instance for application-wide configuration

The configuration supports both environment variables and .env file loading,
with automatic validation and type conversion through Pydantic.
"""

from dotenv import load_dotenv
from pydantic import AmqpDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration management.

    This class manages all configuration parameters for the messaging gRPC server,
    including RabbitMQ connection details, queue configurations, routing keys,
    and server settings. It uses Pydantic for automatic validation and type
    conversion from environment variables.

    Attributes:
        RABBITMQ_HOST (str): RabbitMQ server hostname
        RABBITMQ_PORT (int): RabbitMQ server port number
        RABBITMQ_USER (str): RabbitMQ authentication username
        RABBITMQ_PASSWORD (str): RabbitMQ authentication password
        RABBITMQ_VHOST (str): RabbitMQ virtual host name
        RABBITMQ_EXCHANGE (str): Main exchange name for message routing
        RABBITMQ_EXCHANGE_TYPE (str): Exchange type (topic, direct, fanout)
        RABBITMQ_QUEUE_SCHEMAS (str): Queue name for schema messages
        RABBITMQ_QUEUE_VALIDATIONS (str): Queue name for validation messages
        RABBITMQ_QUEUE_RESULTS_SCHEMAS (str): Queue name for schema results
        RABBITMQ_QUEUE_RESULTS_VALIDATIONS (str): Queue name for validation results
        RABBITMQ_ROUTING_KEY_SCHEMAS (str): Routing key pattern for schema messages
        RABBITMQ_ROUTING_KEY_VALIDATIONS (str): Routing key pattern for validation messages
        RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS (str): Routing key pattern for schema results
        RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS (str): Routing key pattern for validation results
        RABBITMQ_PUBLISHERS_ROUTING_KEY_SCHEMAS (str): Specific routing key for schema publishing
        RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS (str): Specific routing key for validation publishing
        WORKER_CONCURRENCY (int): Number of concurrent worker threads
        WORKER_PREFETCH_COUNT (int): Number of messages to prefetch per worker
        MESSAGING_CONNECTION_HOST (str): gRPC server host address
        MESSAGING_CONNECTION_PORT (int): gRPC server port number
        MESSAGING_CONNECTION_DEBUG (bool): Enable debug mode for detailed logging

    Computed Properties:
        RABBITMQ_URI (AmqpDsn): Complete AMQP connection URI
        MESSAGING_CONNECTION_CHANNEL (str): Complete gRPC connection string

    Notes:
        - Configuration is loaded from environment variables and .env file
        - All RabbitMQ settings are required and must be provided
        - Queue and routing key settings have sensible defaults
        - Debug mode affects logging verbosity and error reporting
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # RabbitMQ Configuration
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str

    @computed_field
    @property
    def RABBITMQ_URI(self) -> AmqpDsn:
        """Generate complete AMQP connection URI.

        Constructs a complete AMQP URI using the configured connection parameters.
        This URI can be used directly with AMQP clients for establishing connections
        to the RabbitMQ server.

        Returns:
            AmqpDsn: Complete AMQP connection URI including credentials and host information

        Example:
            amqp://user:password@localhost:5672/vhost
        """
        return MultiHostUrl.build(
            scheme="amqp",
            username=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD,
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,
        )

    # Messaging Exchanges and Queues
    RABBITMQ_EXCHANGE: str = "typechecking.exchange"
    RABBITMQ_EXCHANGE_TYPE: str = "topic"

    # Queues for different message types
    RABBITMQ_QUEUE_SCHEMAS: str = "typechecking.schemas.queue"
    RABBITMQ_QUEUE_VALIDATIONS: str = "typechecking.validations.queue"
    RABBITMQ_QUEUE_RESULTS_SCHEMAS: str = "typechecking.schemas.results.queue"
    RABBITMQ_QUEUE_RESULTS_VALIDATIONS: str = (
        "typechecking.validation.results.queue"
    )

    # Routing Keys (used for binding queues to the exchange)
    RABBITMQ_ROUTING_KEY_SCHEMAS: str = "schemas.*"
    RABBITMQ_ROUTING_KEY_VALIDATIONS: str = "validation.*"
    RABBITMQ_ROUTING_KEY_RESULTS_SCHEMAS: str = "schemas.result.*"
    RABBITMQ_ROUTING_KEY_RESULTS_VALIDATIONS: str = "validation.result.*"

    # Routing Keys for Publishing (used by producers to send messages)
    RABBITMQ_PUBLISHERS_ROUTING_KEY_SCHEMAS: str = "schemas.update"
    RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS: str = "validation.request"

    # Workers configuration
    WORKER_CONCURRENCY: int = 4
    WORKER_PREFETCH_COUNT: int = 1

    # Messaging Connection Configuration
    MESSAGING_CONNECTION_HOST: str = "localhost"
    MESSAGING_CONNECTION_PORT: int = "50055"
    MESSAGING_CONNECTION_DEBUG: bool = False

    @computed_field
    @property
    def MESSAGING_CONNECTION_CHANNEL(self) -> str:
        """Generate complete gRPC connection channel string.

        Constructs a connection string for gRPC clients to connect to this
        messaging server. The format follows the standard host:port pattern
        used by gRPC client libraries.

        Returns:
            str: Complete gRPC connection string in host:port format

        Example:
            localhost:50055
        """
        return (
            f"{self.MESSAGING_CONNECTION_HOST}:{self.MESSAGING_CONNECTION_PORT}"
        )


settings = Settings()
