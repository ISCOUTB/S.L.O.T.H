from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Minimal server configuration for health checks
    MINIMAL_SERVER_HOST: str = "0.0.0.0"
    MINIMAL_SERVER_PORT: int = 8080
    MINIMAL_SERVER_DEBUG: bool = False

    # RabbitMQ Configuration
    RABBITMQ_MAX_RETRIES: int = 5
    RABBITMQ_RETRY_DELAY_SECONDS: float = 1.0
    RABBITMQ_BACKOFF_MULTIPLIER: float = 2.0
    RABBITMQ_THRESHOLD_SECONDS: float = 60.0

    # Workers Configuration
    MAX_WORKERS: int = 1
    WORKER_PREFETCH_COUNT: int = 1

    # Database connection configuration
    DATABASE_CONNECTION_HOST: str
    DATABASE_CONNECTION_PORT: int
    DATABASE_MAX_RETRIES: int = 5
    DATABASE_RETRY_DELAY_SECONDS: float = 1.0
    DATABASE_BACKOFF_MULTIPLIER: float = 2.0

    @computed_field
    @property
    def DATABASE_CONNECTION_CHANNEL(self) -> str:
        return (
            f"{self.DATABASE_CONNECTION_HOST}:{self.DATABASE_CONNECTION_PORT}"
        )


settings = Settings()
