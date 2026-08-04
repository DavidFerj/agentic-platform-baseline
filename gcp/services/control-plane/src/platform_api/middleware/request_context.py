"""Request correlation context."""

from contextvars import ContextVar, Token
from re import compile as compile_pattern
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_REQUEST_ID = ContextVar[str]("request_id", default="unassigned")
_REQUEST_ID_PATTERN = compile_pattern(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def get_request_id() -> str:
    """Return the request identifier attached to the current async context."""
    return _REQUEST_ID.get()


def normalize_request_id(candidate: str | None) -> str:
    """Preserve a safe identifier or create a non-guessable replacement."""
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Create correlation context and expose it in every response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = normalize_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        token: Token[str] = _REQUEST_ID.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            _REQUEST_ID.reset(token)
