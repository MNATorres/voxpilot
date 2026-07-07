"""Business logic for interpreting voice commands."""

from app.core.logging import get_logger

logger = get_logger("speech")

# Maps a recognized voice command to the action log it produces.
COMMANDS: dict[str, str] = {
    "camina hacia adelante": "caminó hacia adelante",
}


class SpeechService:
    """Interprets a voice command and logs the resulting action."""

    def process(self, command: str) -> dict[str, object]:
        """Interpret ``command``, log the action and return the outcome."""
        normalized = command.strip().lower()
        action = COMMANDS.get(normalized)

        if action is None:
            logger.info("comando no reconocido", recibido=command)
            return {"recognized": False, "action": None}

        logger.info(action, recibido=command)
        return {"recognized": True, "action": action}
