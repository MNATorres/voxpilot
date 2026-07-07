"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import get_settings


def create_app() -> FastAPI:
    """Application factory: build and configure the FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
    )

    return app


app = create_app()
