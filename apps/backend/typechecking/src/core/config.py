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
    RABBITMQ_VHOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    @computed_field
    @property
    def RABBITMQ_URI(self) -> AmqpDsn:
        return MultiHostUrl.build(
            scheme="amqp",
            username=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD,
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,
            path=self.RABBITMQ_VHOST,
        )

    # Workers Configuration
    MAX_WORKERS: int = 1
    WORKER_CONCURRENCY: int = 4
    WORKER_PREFETCH_COUNT: int = 1

    # Database connection configuration
    DATABASE_CONNECTION_HOST: str
    DATABASE_CONNECTION_PORT: int

    @computed_field
    @property
    def DATABASE_CONNECTION_CHANNEL(self) -> str:
        return (
            f"{self.DATABASE_CONNECTION_HOST}:{self.DATABASE_CONNECTION_PORT}"
        )


settings = Settings()
