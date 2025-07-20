import secrets

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    computed_field,
    BeforeValidator,
    AmqpDsn,
    MongoDsn,
    PostgresDsn,
    RedisDsn,
)

from typing import Any, Annotated

from dotenv import load_dotenv

load_dotenv()


def split_list(v: Any) -> list[str] | str:
    """
    Función para dividir cadenas en una lista en formato de texto.

    Args:
        v (Any): Valor que puede ser una cadena o lista.

    Returns:
        list[str] | str: Lista o la cadena original si ya es una lista o cadena respectivamente.

    Raises:
        ValueError: Si el valor no es de tipo válido.
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

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day by default

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

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

    # MongoDB Configuration
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_INITDB_ROOT_USERNAME: str | None = None
    MONGO_INITDB_ROOT_PASSWORD: str | None = None
    MONGO_DB: str
    MONGO_COLLECTION: str

    @computed_field
    @property
    def MONGO_URI(self) -> MongoDsn:
        return MultiHostUrl.build(
            scheme="mongodb",
            username=self.MONGO_INITDB_ROOT_USERNAME,
            password=self.MONGO_INITDB_ROOT_PASSWORD,
            host=self.MONGO_HOST,
            port=self.MONGO_PORT,
        )

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str
    REDIS_EXPIRE_SECONDS: int = 60 * 5  # 5 minutes by default

    @computed_field
    @property
    def REDIS_URI(self) -> RedisDsn:
        return MultiHostUrl.build(
            scheme="redis",
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
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


settings = Settings()
