from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, MongoDsn, RedisDsn

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # MongoDB Configuration
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_INITDB_ROOT_USERNAME: str | None = None
    MONGO_INITDB_ROOT_PASSWORD: str | None = None
    MONGO_DB: str
    MONGO_SCHEMAS_COLLECTION: str
    MONGO_TASKS_COLLECTION: str

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

    # Database Connection Configuration
    DATABASE_CONNECTION_HOST: str
    DATABASE_CONNECTION_PORT: int
    DATABASE_CONNECTION_DEBUG: bool = False

    @computed_field
    @property
    def DATABASE_CONNECTION_CHANNEL(self) -> str:
        return f"{self.DATABASE_CONNECTION_HOST}:{self.DATABASE_CONNECTION_PORT}"


settings = Settings()
