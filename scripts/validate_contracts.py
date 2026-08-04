"""Validate versioned HTTP and event contracts."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from openapi_spec_validator import validate
from yaml import safe_load

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate contract syntax against authoritative schemas."""
    openapi_path = ROOT / "gcp/packages/contracts/openapi/control-plane.v1.yaml"
    with openapi_path.open(encoding="utf-8") as source:
        validate(safe_load(source))

    event_path = ROOT / "gcp/packages/contracts/events/envelope.v1.schema.json"
    with event_path.open(encoding="utf-8") as source:
        Draft202012Validator.check_schema(json.load(source))


if __name__ == "__main__":
    main()
