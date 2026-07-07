"""Structured logging configuration (structlog)."""

import logging

import structlog
from asgi_correlation_id import correlation_id
from structlog.typing import EventDict, WrappedLogger


def _add_correlation_id(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Inject the current request's correlation id into every log line."""
    event_dict["correlation_id"] = correlation_id.get() or "-"
    return event_dict


def configure_logging() -> None:
    """Configure structlog for clear, real-time, structured output.

    Every log line carries the date, level and correlation id. Safe to call
    once at startup.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_correlation_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to ``name``."""
    return structlog.get_logger(name)
