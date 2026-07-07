"""Pydantic schemas for the speech endpoint."""

from pydantic import BaseModel


class SpeechRequest(BaseModel):
    """Request body carrying a voice command."""

    command: str


class SpeechResponse(BaseModel):
    """Result of interpreting a voice command."""

    recognized: bool
    action: str | None
