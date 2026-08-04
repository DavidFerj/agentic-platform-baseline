from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from platform_api.api.app import create_app
from platform_api.core.config import AuthMode, Environment, Settings


class FakeDatabase:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.ping_count = 0
        self.dispose_count = 0

    async def ping(self) -> None:
        self.ping_count += 1
        if self.error is not None:
            raise self.error

    async def dispose(self) -> None:
        self.dispose_count += 1


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "environment": Environment.TEST,
        "auth_mode": AuthMode.DEVELOPMENT,
        "database_url": "sqlite+aiosqlite:///:memory:",
        "cors_origins": "",
        "docs_enabled": False,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


@pytest.fixture
def fake_database() -> FakeDatabase:
    return FakeDatabase()


@pytest.fixture
def client(fake_database: FakeDatabase) -> Iterator[TestClient]:
    app = create_app(settings=make_settings(), database=fake_database)
    with TestClient(app) as test_client:
        yield test_client
