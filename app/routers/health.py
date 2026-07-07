"""Health check route definitions."""

from fastapi import APIRouter

from app.controllers.health_controller import HealthController
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])

_controller = HealthController()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return the service health status."""
    return HealthResponse(**_controller.check())
