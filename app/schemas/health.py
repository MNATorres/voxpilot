"""Pydantic schemas for the health endpoint."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    status: str
    service: str
    version: str
