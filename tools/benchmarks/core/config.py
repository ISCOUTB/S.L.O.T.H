from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    computed_field,
    PostgresDsn,
)

from typing import Any

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
