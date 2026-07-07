"""Unit tests for application settings."""

from app.core.config import Settings, get_settings


def test_settings_values():
    settings = get_settings()

    assert settings.app_name == "VoxPilot"
    assert settings.version == "0.1.0"
    assert settings.description


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_settings_can_be_instantiated_directly():
    assert isinstance(Settings(), Settings)
