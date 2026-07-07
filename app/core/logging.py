"""Logging configuration."""

import logging


def configure_logging() -> None:
    """Configure application-wide logging.

    Uses a simple stdout handler; safe to call once at startup.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger under the ``voxpilot`` namespace."""
    return logging.getLogger(f"voxpilot.{name}")
