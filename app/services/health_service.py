"""Business logic for the health check."""

from app.core.config import get_settings


class HealthService:
    """Produces the service health status."""

    def get_status(self) -> dict[str, str]:
        """Return the current health status of the service."""
        settings = get_settings()
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.version,
        }
