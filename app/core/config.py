"""Application configuration."""

from functools import lru_cache


class Settings:
    """Central application settings.

    Kept intentionally minimal for now; extend as the app grows
    (env-backed values, external service credentials, etc.).
    """

    app_name: str = "VoxPilot"
    version: str = "0.1.0"
    description: str = "Voice-controlled action pilot API"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
