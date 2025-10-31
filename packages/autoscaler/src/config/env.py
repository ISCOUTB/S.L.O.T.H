from pydantic_settings import BaseSettings, SettingsConfigDict
from src.utils import ROOTDIR


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOTDIR / ".env").absolute(),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


env = EnvSettings()

if __name__ == "__main__":
    pass
