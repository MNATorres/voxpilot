"""Voice command route definitions."""

from fastapi import APIRouter

from app.controllers.speech_controller import SpeechController
from app.schemas.speech import SpeechRequest, SpeechResponse

router = APIRouter(tags=["speech"])

_controller = SpeechController()


@router.post("/speak", response_model=SpeechResponse)
def speak(payload: SpeechRequest) -> SpeechResponse:
    """Receive a voice command and trigger the matching action."""
    return SpeechResponse(**_controller.handle(payload.command))
