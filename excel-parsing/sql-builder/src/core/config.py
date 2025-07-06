from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    SQL_BUILDER_HOST: str = "localhost"
    SQL_BUILDER_PORT: str = "50054"
    SQL_BUILDER_DEBUG: bool = False

    @computed_field
    @property
    def SQL_BUILDER_CHANNEL(self) -> str:
        return f"{self.SQL_BUILDER_HOST}:{self.SQL_BUILDER_PORT}"


settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
