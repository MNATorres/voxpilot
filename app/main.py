"""FastAPI application entry point."""

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routers import health, speech


def create_app() -> FastAPI:
    """Application factory: build and configure the FastAPI instance."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
    )

    # Generates/propagates a correlation id per request (X-Request-ID header).
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(health.router)
    app.include_router(speech.router)

    return app


app = create_app()
