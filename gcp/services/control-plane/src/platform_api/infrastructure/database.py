"""Async SQLAlchemy database lifecycle."""

from typing import Any, Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


class DatabaseGateway(Protocol):
    """Operational database behavior consumed by the application."""

    async def ping(self) -> None:
        """Raise when the database cannot serve a trivial query."""
        ...

    async def dispose(self) -> None:
        """Release connection pools."""
        ...


class Database:
    """Owned SQLAlchemy engine and session factory."""

    def __init__(
        self,
        database_url: str,
        *,
        pool_size: int = 5,
        max_overflow: int = 5,
        pool_timeout_seconds: int = 5,
        statement_timeout_ms: int = 15_000,
    ) -> None:
        engine_options: dict[str, Any] = {"pool_pre_ping": True}
        if database_url.startswith("postgresql"):
            engine_options.update(
                {
                    "pool_size": pool_size,
                    "max_overflow": max_overflow,
                    "pool_timeout": pool_timeout_seconds,
                    "pool_recycle": 300,
                    "connect_args": {
                        "server_settings": {
                            "statement_timeout": str(statement_timeout_ms),
                        }
                    },
                }
            )
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            **engine_options,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    async def ping(self) -> None:
        """Verify database connectivity without exposing connection details."""
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def dispose(self) -> None:
        """Dispose the engine connection pool."""
        await self.engine.dispose()
