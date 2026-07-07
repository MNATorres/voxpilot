"""Unit tests for HealthService."""

from app.services.health_service import HealthService


def test_get_status_returns_ok():
    result = HealthService().get_status()

    assert result == {
        "status": "ok",
        "service": "VoxPilot",
        "version": "0.1.0",
    }
