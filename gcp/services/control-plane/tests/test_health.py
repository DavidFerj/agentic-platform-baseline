from conftest import FakeDatabase, make_settings
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from platform_api.api.app import create_app


def test_liveness_preserves_a_safe_request_id(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "trace-123"})

    assert response.status_code == 200
    assert response.json() == {"status": "live", "dependencies": {}}
    assert response.headers["X-Request-ID"] == "trace-123"


def test_liveness_replaces_an_unsafe_request_id(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "unsafe value\n"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "unsafe value"
    assert len(response.headers["X-Request-ID"]) == 36


def test_liveness_generates_a_missing_request_id(client: TestClient) -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert len(response.headers["X-Request-ID"]) == 36


def test_readiness_reports_database_state(
    client: TestClient,
    fake_database: FakeDatabase,
) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {"database": "ready"},
    }
    assert fake_database.ping_count == 1


def test_readiness_hides_database_failure_details() -> None:
    database = FakeDatabase(SQLAlchemyError("postgresql://user:secret@example.invalid"))
    app = create_app(settings=make_settings(), database=database)

    with TestClient(app) as client:
        response = client.get("/health/ready", headers={"X-Request-ID": "ready-check"})

    assert response.status_code == 503
    assert response.json() == {
        "type": "urn:agentic-platform:error:database_unavailable",
        "title": "Service unavailable",
        "status": 503,
        "detail": "A required data service is unavailable.",
        "code": "database_unavailable",
        "request_id": "ready-check",
    }
    assert "secret" not in response.text
