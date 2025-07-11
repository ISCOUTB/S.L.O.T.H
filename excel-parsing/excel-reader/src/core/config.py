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

    FORMULA_PARSER_HOST: str = "localhost"
    FORMULA_PARSER_PORT: str = "50052"

    @computed_field
    @property
    def FORMULA_PARSER_CHANNEL(self) -> str:
        return f"{self.FORMULA_PARSER_HOST}:{self.FORMULA_PARSER_PORT}"

    DDL_GENERATOR_HOST: str = "localhost"
    DDL_GENERATOR_PORT: str = "50053"

    @computed_field
    @property
    def DDL_GENERATOR_CHANNEL(self) -> str:
        return f"{self.DDL_GENERATOR_HOST}:{self.DDL_GENERATOR_PORT}"
    
    SQL_BUILDER_HOST: str = "localhost"
    SQL_BUILDER_PORT: str = "50054"

    @computed_field
    @property
    def SQL_BUILDER_CHANNEL(self) -> str:
        return f"{self.SQL_BUILDER_HOST}:{self.SQL_BUILDER_PORT}"
    
    EXCEL_READER_HOST: str = "localhost"
    EXCEL_READER_PORT: int = 8001
    EXCEL_READER_DEBUG: bool = False


settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
