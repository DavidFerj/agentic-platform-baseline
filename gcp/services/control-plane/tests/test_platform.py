from fastapi.testclient import TestClient


def test_platform_information_reports_only_foundation_capabilities(client: TestClient) -> None:
    response = client.get("/api/v1/platform")

    assert response.status_code == 200
    body = response.json()
    assert body["product"] == "Agentic Platform Baseline"
    assert body["short_name"] == "APB"
    assert body["version"] == "0.1.0"
    assert body["phase"] == "foundation"
    assert "operational-api" in body["implemented_capabilities"]
    assert "agent-orchestration" in body["deferred_capabilities"]
    assert "multi-tenant foundation" in body["north_star"]
