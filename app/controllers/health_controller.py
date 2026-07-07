"""Controller layer for the health check."""

from app.services.health_service import HealthService


class HealthController:
    """Handles health requests and delegates to the service layer."""

    def __init__(self, service: HealthService | None = None) -> None:
        self._service = service or HealthService()

    def check(self) -> dict[str, str]:
        """Return the health status produced by the service."""
        return self._service.get_status()
