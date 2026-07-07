"""Unit tests for SpeechController."""

from app.controllers.speech_controller import SpeechController


class _FakeSpeechService:
    def __init__(self) -> None:
        self.received: str | None = None

    def process(self, command: str) -> dict[str, object]:
        self.received = command
        return {"recognized": True, "action": "sentinel"}


def test_handle_delegates_and_forwards_command():
    service = _FakeSpeechService()
    controller = SpeechController(service=service)

    result = controller.handle("camina hacia adelante")

    assert service.received == "camina hacia adelante"
    assert result == {"recognized": True, "action": "sentinel"}


def test_handle_uses_real_service_by_default():
    result = SpeechController().handle("camina hacia adelante")

    assert result == {"recognized": True, "action": "caminó hacia adelante"}
