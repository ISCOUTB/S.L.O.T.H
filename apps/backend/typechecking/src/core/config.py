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
