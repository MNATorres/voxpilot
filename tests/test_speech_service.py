"""Unit tests for SpeechService."""

import pytest

from app.services import speech_service
from app.services.speech_service import SpeechService


class _FakeLogger:
    """Records logging calls for assertion."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def info(self, event: str, **kwargs) -> None:
        self.calls.append((event, kwargs))


@pytest.fixture
def fake_logger(monkeypatch):
    logger = _FakeLogger()
    monkeypatch.setattr(speech_service, "logger", logger)
    return logger


def test_recognized_command_returns_action(fake_logger):
    result = SpeechService().process("camina hacia adelante")

    assert result == {"recognized": True, "action": "caminó hacia adelante"}


def test_recognized_command_logs_action_and_received(fake_logger):
    SpeechService().process("camina hacia adelante")

    event, kwargs = fake_logger.calls[0]
    assert event == "caminó hacia adelante"
    assert kwargs["recibido"] == "camina hacia adelante"


@pytest.mark.parametrize(
    "raw",
    [
        "camina hacia adelante",
        "  camina hacia adelante  ",
        "CAMINA HACIA ADELANTE",
        "Camina Hacia Adelante",
    ],
)
def test_command_is_normalized(fake_logger, raw):
    result = SpeechService().process(raw)

    assert result["recognized"] is True
    assert result["action"] == "caminó hacia adelante"


def test_unknown_command_returns_not_recognized(fake_logger):
    result = SpeechService().process("salta")

    assert result == {"recognized": False, "action": None}


def test_unknown_command_logs_received(fake_logger):
    SpeechService().process("salta")

    event, kwargs = fake_logger.calls[0]
    assert event == "comando no reconocido"
    assert kwargs["recibido"] == "salta"
