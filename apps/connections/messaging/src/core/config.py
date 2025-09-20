from dotenv import load_dotenv
from pydantic import AmqpDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
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
    WORKER_CONCURRENCY = 4
    WORKER_PREFETCH_COUNT = 1

    # Messaging Connection Configuration
    MESSAGING_CONNECTION_HOST: str
    MESSAGING_CONNECTION_PORT: int
    MESSAGING_CONNECTION_DEBUG: bool = False

    @computed_field
    @property
    def MESSAGING_CONNECTION_CHANNEL(self) -> str:
        return (
            f"{self.MESSAGING_CONNECTION_HOST}:{self.MESSAGING_CONNECTION_PORT}"
        )


settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
