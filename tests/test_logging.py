"""Unit tests for the logging configuration."""

from asgi_correlation_id import correlation_id

from app.core.logging import _add_correlation_id, configure_logging, get_logger


def test_add_correlation_id_defaults_to_dash():
    event = _add_correlation_id(None, "info", {})

    assert event["correlation_id"] == "-"


def test_add_correlation_id_uses_current_value():
    token = correlation_id.set("abc-123")
    try:
        event = _add_correlation_id(None, "info", {})
    finally:
        correlation_id.reset(token)

    assert event["correlation_id"] == "abc-123"


def test_configure_logging_does_not_raise():
    configure_logging()


def test_get_logger_returns_a_usable_logger():
    logger = get_logger("test")

    assert hasattr(logger, "info")
