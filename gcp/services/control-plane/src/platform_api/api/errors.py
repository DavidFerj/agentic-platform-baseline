"""Safe public error mapping."""

import logging
from dataclasses import dataclass
from pathlib import Path
from traceback import extract_tb

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from platform_api.contracts.operational import ProblemDetail
from platform_api.middleware.request_context import get_request_id

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ApplicationError(Exception):
    """An expected application failure with a safe external representation."""

    status_code: int
    code: str
    title: str
    detail: str


class ServiceUnavailableError(ApplicationError):
    """A required dependency is temporarily unavailable."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(
            status_code=503,
            code=code,
            title="Service unavailable",
            detail=detail,
        )


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", get_request_id())


def _response(error: ApplicationError, request_id: str) -> JSONResponse:
    body = ProblemDetail(
        type=f"urn:agentic-platform:error:{error.code}",
        title=error.title,
        status=error.status_code,
        detail=error.detail,
        code=error.code,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=error.status_code,
        content=body.model_dump(mode="json"),
        headers={"X-Request-ID": request_id},
    )


async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
    """Map an expected error to the public problem-details contract."""
    return _response(error, _request_id(request))


async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
    """Log an unexpected cause and return a non-sensitive response."""
    stack_frames = [
        {
            "file": Path(frame.filename).name,
            "function": frame.name,
            "line": frame.lineno,
        }
        for frame in extract_tb(error.__traceback__)
    ]
    logger.error(
        "Unhandled API exception",
        extra={
            "exception_type": type(error).__name__,
            "request_id": _request_id(request),
            "stack_frames": stack_frames,
        },
    )
    return _response(
        ApplicationError(
            status_code=500,
            code="internal_error",
            title="Internal server error",
            detail="The request could not be completed.",
        ),
        _request_id(request),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Install application and defensive boundary exception handlers."""
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unexpected_error_handler)
