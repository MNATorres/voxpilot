"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import health


def create_app() -> FastAPI:
    """Application factory: build and configure the FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
    )

    app.include_router(health.router)

    return app


app = create_app()
