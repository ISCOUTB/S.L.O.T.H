from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    DDL_GENERATOR_HOST: str = "localhost"
    DDL_GENERATOR_PORT: str = "50053"
    DDL_GENERATOR_DEBUG: bool = False

    @computed_field
    @property
    def DDL_GENERATOR_CHANNEL(self) -> str:
        return f"{self.DDL_GENERATOR_HOST}:{self.DDL_GENERATOR_PORT}"


settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
