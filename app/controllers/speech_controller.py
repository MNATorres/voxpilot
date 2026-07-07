"""Controller layer for voice commands."""

from app.services.speech_service import SpeechService


class SpeechController:
    """Handles speech requests and delegates to the service layer."""

    def __init__(self, service: SpeechService | None = None) -> None:
        self._service = service or SpeechService()

    def handle(self, command: str) -> dict[str, object]:
        """Process a voice command and return the outcome."""
        return self._service.process(command)
