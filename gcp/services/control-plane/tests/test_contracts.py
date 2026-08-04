import json
from pathlib import Path

import pytest
from conftest import FakeDatabase, make_settings
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as JsonSchemaValidationError
from openapi_spec_validator import validate
from pydantic import ValidationError
from yaml import safe_load

from platform_api.api.app import create_app
from platform_api.contracts.operational import HealthResponse

ROOT = Path(__file__).resolve().parents[4]


def test_versioned_openapi_contract_is_valid_and_matches_routes() -> None:
    contract_path = ROOT / "gcp/packages/contracts/openapi/control-plane.v1.yaml"
    contract = safe_load(contract_path.read_text(encoding="utf-8"))
    validate(contract)

    implementation = create_app(
        settings=make_settings(),
        database=FakeDatabase(),
    ).openapi()

    assert set(contract["paths"]) == {
        "/health/live",
        "/health/ready",
        "/api/v1/platform",
    }
    assert set(contract["paths"]).issubset(implementation["paths"])


def test_event_envelope_schema_is_valid_json() -> None:
    event_path = ROOT / "gcp/packages/contracts/events/envelope.v1.schema.json"
    schema = json.loads(event_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)

    event = {
        "event_id": "a3816945-4240-4c42-a1ae-45124bd315f1",
        "event_type": "projection.requested",
        "occurred_at": "2026-07-29T12:00:00Z",
        "tenant_id": "35ec55a5-1abc-4cd8-8c29-e58b391641c6",
        "correlation_id": "request-123",
        "producer": "control-plane",
        "schema_version": 1,
        "idempotency_key": "projection:project-123:4",
        "aggregate_type": "project",
        "aggregate_id": "project-123",
        "aggregate_version": 4,
        "data": {"status": "ready"},
    }

    Draft202012Validator(schema).validate(event)
    assert schema["additionalProperties"] is False

    del event["idempotency_key"]
    with pytest.raises(JsonSchemaValidationError):
        Draft202012Validator(schema).validate(event)


def test_public_models_reject_undocumented_fields() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="live", dependencies={}, undocumented=True)  # type: ignore[call-arg]
