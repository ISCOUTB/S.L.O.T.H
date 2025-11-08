import secrets
from typing import Annotated, Any

from dotenv import load_dotenv
from pydantic import (
    AmqpDsn,
    BeforeValidator,
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


def split_list(v: Any) -> list[str] | str:
    """
    Function to split strings into a list in text format.

    Args:
        v (Any): Value that can be a string or list.

    Returns:
        list[str] | str: List or the original string if it's already a list or string respectively.

    Raises:
        ValueError: If the value is not of a valid type.
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    # API Configuration
    API_V1_STR: str
    CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(split_list)]
    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_DEBUG: bool

    SECRET_KEY: str = secrets.token_urlsafe(32)

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # RabbitMQ Configuration
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_VHOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_MAX_RETRIES: int = 5
    RABBITMQ_RETRY_DELAY_SECONDS: float = 1.0
    RABBITMQ_BACKOFF_MULTIPLIER: float = 2.0

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

    # PostgreSQL Configuration
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def POSTGRES_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Database Connection Configuration
    DATABASE_CONNECTION_HOST: str
    DATABASE_CONNECTION_PORT: int

    @computed_field
    @property
    def DATABASE_CONNECTION_CHANNEL(self) -> str:
        return f"{self.DATABASE_CONNECTION_HOST}:{self.DATABASE_CONNECTION_PORT}"


settings = Settings()
