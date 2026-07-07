"""Unit tests for HealthController."""

from app.controllers.health_controller import HealthController


class _FakeHealthService:
    def get_status(self) -> dict[str, str]:
        return {"status": "sentinel"}


def test_check_delegates_to_service():
    controller = HealthController(service=_FakeHealthService())

    assert controller.check() == {"status": "sentinel"}


def test_check_uses_real_service_by_default():
    result = HealthController().check()

    assert result["status"] == "ok"
    assert result["service"] == "VoxPilot"
