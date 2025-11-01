from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils.rootdir import ROOTDIR


class EnvSettings(BaseSettings):
    DEBUG: bool = False
    
    PROMETHEUS_URL: str = "http://prometheus:9090/"

    STACK_NAME: str = str(...)
    CHECK_INVERVAL: int = 30
    COOLDOWN_PERIOD: int = 180
    DEFAULT_MIN_REPLICAS: int = 1
    DEFAULT_MAX_REPLICAS: int = 10

    model_config = SettingsConfigDict(
        env_file=(ROOTDIR / ".env").absolute(),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


env = EnvSettings()

if __name__ == "__main__":
    pass
