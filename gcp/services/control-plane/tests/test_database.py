import pytest

from platform_api.infrastructure import database as database_module
from platform_api.infrastructure.database import Database


@pytest.mark.asyncio
async def test_database_ping_and_dispose() -> None:
    database = Database("sqlite+aiosqlite:///:memory:")

    await database.ping()
    await database.dispose()


def test_postgres_database_uses_bounded_pool_and_statement_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_create_async_engine(url: str, **options: object) -> object:
        captured["url"] = url
        captured["options"] = options
        return object()

    monkeypatch.setattr(database_module, "create_async_engine", fake_create_async_engine)

    Database(
        "postgresql+asyncpg://runtime:secret@postgres/platform",
        pool_size=7,
        max_overflow=3,
        pool_timeout_seconds=4,
        statement_timeout_ms=12_000,
    )

    assert captured == {
        "url": "postgresql+asyncpg://runtime:secret@postgres/platform",
        "options": {
            "pool_pre_ping": True,
            "pool_size": 7,
            "max_overflow": 3,
            "pool_timeout": 4,
            "pool_recycle": 300,
            "connect_args": {"server_settings": {"statement_timeout": "12000"}},
        },
    }
