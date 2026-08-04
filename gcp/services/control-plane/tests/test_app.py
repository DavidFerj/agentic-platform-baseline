from conftest import FakeDatabase, make_settings
from fastapi import FastAPI
from fastapi.testclient import TestClient

from platform_api.api.app import create_app
from platform_api.core.config import AuthMode, Environment


def test_application_factory_owns_default_database(monkeypatch) -> None:
    monkeypatch.setenv("PLATFORM_ENVIRONMENT", Environment.TEST)
    monkeypatch.setenv("PLATFORM_AUTH_MODE", AuthMode.DEVELOPMENT)
    monkeypatch.setenv("PLATFORM_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("PLATFORM_DOCS_ENABLED", "false")

    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert app.docs_url is None
    assert app.openapi_url is None


def test_application_factory_keeps_injected_database_and_enables_cors() -> None:
    database = FakeDatabase()
    app = create_app(
        settings=make_settings(
            cors_origins="http://localhost:3000",
            docs_enabled=True,
        ),
        database=database,
    )

    with TestClient(app) as client:
        response = client.options(
            "/api/v1/platform",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert app.docs_url == "/docs"
    assert database.dispose_count == 0


def test_unexpected_errors_use_a_safe_problem_contract(capsys) -> None:
    app: FastAPI = create_app(settings=make_settings(), database=FakeDatabase())

    @app.get("/explode")
    async def explode() -> None:
        raise RuntimeError("postgresql://user:secret@example.invalid")

    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get("/explode", headers={"X-Request-ID": "safe-request"})

    logs = capsys.readouterr().err
    assert response.status_code == 500
    assert response.json() == {
        "type": "urn:agentic-platform:error:internal_error",
        "title": "Internal server error",
        "status": 500,
        "detail": "The request could not be completed.",
        "code": "internal_error",
        "request_id": "safe-request",
    }
    assert "secret" not in response.text
    assert "secret" not in logs
    assert "Unhandled API exception" in logs
    assert '"function": "explode"' in logs
