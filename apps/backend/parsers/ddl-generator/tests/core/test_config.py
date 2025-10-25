from pytest import MonkeyPatch

from core.config import Settings


def test_settings_defaults():
    s = Settings()

    assert s.DDL_GENERATOR_HOST == "localhost"
    assert s.DDL_GENERATOR_PORT == "50053"
    assert s.DDL_GENERATOR_DEBUG is False


def test_ddl_generator_channel_property():
    s = Settings()
    expected = f"{s.DDL_GENERATOR_HOST}:{s.DDL_GENERATOR_PORT}"
    assert s.DDL_GENERATOR_CHANNEL == expected


def test_settings_env_override(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("DDL_GENERATOR_HOST", "otrohost")
    monkeypatch.setenv("DDL_GENERATOR_PORT", "12345")
    monkeypatch.setenv("DDL_GENERATOR_DEBUG", "true")

    s = Settings()

    assert s.DDL_GENERATOR_HOST == "otrohost"
    assert s.DDL_GENERATOR_PORT == "12345"
    assert s.DDL_GENERATOR_DEBUG is True
    assert s.DDL_GENERATOR_CHANNEL == "otrohost:12345"
