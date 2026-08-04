"""Structured logging configuration."""

import logging

from pythonjsonlogger.json import JsonFormatter

from platform_api.middleware.request_context import get_request_id


class RequestIdFilter(logging.Filter):
    """Attach correlation context to every structured record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__.setdefault("request_id", get_request_id())
        return True


def configure_logging(level: str) -> None:
    """Configure a deterministic JSON root logger."""
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
    )
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        child_logger = logging.getLogger(logger_name)
        child_logger.handlers.clear()
        child_logger.propagate = True
