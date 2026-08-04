"""FastAPI application composition."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from platform_api import __version__
from platform_api.api.errors import register_error_handlers
from platform_api.api.routes.health import router as health_router
from platform_api.api.routes.platform import router as platform_router
from platform_api.core.config import Settings
from platform_api.core.logging import configure_logging
from platform_api.infrastructure.database import Database, DatabaseGateway
from platform_api.middleware.request_context import RequestContextMiddleware


def create_app(
    settings: Settings | None = None,
    database: DatabaseGateway | None = None,
) -> FastAPI:
    """Create a configured API instance with explicit replaceable dependencies."""
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.log_level)

    owns_database = database is None
    resolved_database = database or Database(
        resolved_settings.database_url,
        pool_size=resolved_settings.database_pool_size,
        max_overflow=resolved_settings.database_max_overflow,
        pool_timeout_seconds=resolved_settings.database_pool_timeout_seconds,
        statement_timeout_ms=resolved_settings.database_statement_timeout_ms,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        if owns_database:
            await resolved_database.dispose()

    app = FastAPI(
        title=resolved_settings.product_name,
        version=__version__,
        description="Human-governed vertical-agnostic agentic delivery control plane.",
        docs_url="/docs" if resolved_settings.api_docs_enabled else None,
        redoc_url="/redoc" if resolved_settings.api_docs_enabled else None,
        openapi_url="/openapi.json" if resolved_settings.api_docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.database = resolved_database

    app.add_middleware(RequestContextMiddleware)
    origins = resolved_settings.cors_origin_list
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(origins),
            allow_credentials=True,
            allow_methods=["GET"],
            allow_headers=["Accept", "Content-Type", "X-Request-ID"],
        )

    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(platform_router, prefix="/api/v1")
    return app
