"""Validate repository and Firebase architecture invariants."""

import json
import re
import tomllib
from pathlib import Path

from yaml import safe_load

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "LICENSE",
    "NOTICE",
    ".gcloudignore",
    ".githooks/pre-commit",
    ".githooks/pre-push",
    "frontend/package.json",
    "frontend/apphosting.yaml",
    "turbo.json",
    "gcp/services/control-plane/pyproject.toml",
    "gcp/services/orchestrator/README.md",
    "gcp/functions/README.md",
    "gcp/jobs/README.md",
    "gcp/packages/contracts/package.json",
    "gcp/firebase/firestore.rules",
    "gcp/firebase/firestore.indexes.json",
    "gcp/infrastructure/terraform/README.md",
    "gcp/infrastructure/postgres/init/001-runtime-role.sh",
    "docs/adrs/0008-reliable-cross-store-events.md",
    "docs/adrs/0009-external-identity-mapping.md",
    "docs/architecture/data-governance.md",
    "docs/adrs/0011-deterministic-data-protection-control-plane.md",
    "docs/compliance/applicability-matrix.yaml",
    "docs/compliance/control-catalog.yaml",
    "docs/compliance/data-inventory.yaml",
    "gcp/packages/contracts/compliance/policy-decision.v1.schema.json",
    "specs/data-protection-foundation/requirements.md",
    "docs/runbooks/cross-store-recovery.md",
    "docs/runbooks/secret-management.md",
    "docs/adrs/0010-keyless-github-to-gcp-authentication.md",
    ".github/CODEOWNERS.example",
    "template.config.example.json",
    "scripts/bootstrap_template.py",
    "specs/template-foundation/requirements.md",
    ".github/pull_request_template.md",
    "SECURITY.md",
    "firebase.json",
    "scripts/validate_repository_hygiene.py",
)
FORBIDDEN_LEGACY_DIRECTORIES = ("apps", "packages", "services", "infrastructure")


def main() -> None:
    """Fail when required boundaries or fail-closed Firebase defaults drift."""
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        raise ValueError(f"missing architecture paths: {', '.join(missing)}")

    legacy = [path for path in FORBIDDEN_LEGACY_DIRECTORIES if (ROOT / path).exists()]
    if legacy:
        raise ValueError(f"legacy root directories remain: {', '.join(legacy)}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
        raise ValueError("repository license must contain the canonical Apache-2.0 terms")

    package_manifests = (
        "package.json",
        "frontend/package.json",
        "gcp/firebase/package.json",
        "gcp/packages/contracts/package.json",
    )
    if any(
        json.loads((ROOT / path).read_text(encoding="utf-8")).get("license") != "Apache-2.0"
        for path in package_manifests
    ):
        raise ValueError("JavaScript package metadata must declare Apache-2.0")

    control_plane_metadata = tomllib.loads(
        (ROOT / "gcp/services/control-plane/pyproject.toml").read_text(encoding="utf-8")
    )
    if control_plane_metadata["project"].get("license") != "Apache-2.0":
        raise ValueError("Python package metadata must declare Apache-2.0")

    firebase_config = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))
    firestore = firebase_config["firestore"]
    if firestore["rules"] != "gcp/firebase/firestore.rules":
        raise ValueError("Firebase config must reference the versioned Firestore rules")
    if firebase_config["emulators"]["apphosting"]["rootDirectory"] != "frontend":
        raise ValueError("App Hosting emulator must target the frontend root")
    if firebase_config["emulators"]["apphosting"]["startCommand"] != "pnpm run dev":
        raise ValueError("App Hosting emulator must use the explicit frontend start command")

    app_hosting = safe_load((ROOT / "frontend/apphosting.yaml").read_text(encoding="utf-8"))
    run_config = app_hosting["runConfig"]
    if run_config["minInstances"] != 0 or run_config["maxInstances"] < 1:
        raise ValueError("App Hosting defaults must scale to zero and retain a positive cap")

    firestore_rules = (ROOT / "gcp/firebase/firestore.rules").read_text(encoding="utf-8")
    required_rules = (
        "request.auth.token.firebase.tenant == tenantId",
        "runProjections",
        "projectProjections",
        "allow write: if false;",
        "allow read, write: if false;",
    )
    if any(rule not in firestore_rules for rule in required_rules):
        raise ValueError("Firestore rules lost a required tenant or deny-by-default control")

    compose = safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    services = compose["services"]
    runtime_url = services["api"]["environment"]["PLATFORM_DATABASE_URL"]
    migration_url = services["migrate"]["environment"]["PLATFORM_DATABASE_URL"]
    if "${POSTGRES_APP_USER}" not in runtime_url or "${POSTGRES_APP_PASSWORD}" not in runtime_url:
        raise ValueError("API must use the non-owner PostgreSQL runtime identity")
    if "${POSTGRES_USER}" not in migration_url or "${POSTGRES_PASSWORD}" not in migration_url:
        raise ValueError("migration job must use the PostgreSQL owner identity")
    if services["api"]["depends_on"]["migrate"]["condition"] != "service_completed_successfully":
        raise ValueError("API must wait for the one-shot migration job")

    role_script = (ROOT / "gcp/infrastructure/postgres/init/001-runtime-role.sh").read_text(
        encoding="utf-8"
    )
    if "NOSUPERUSER" not in role_script or "NOBYPASSRLS" not in role_script:
        raise ValueError("local runtime role must not bypass PostgreSQL security boundaries")

    event_schema = json.loads(
        (ROOT / "gcp/packages/contracts/events/envelope.v1.schema.json").read_text(encoding="utf-8")
    )
    event_requirements = {
        "idempotency_key",
        "aggregate_type",
        "aggregate_id",
        "aggregate_version",
    }
    if not event_requirements.issubset(event_schema["required"]):
        raise ValueError("event envelope lost idempotency or aggregate ordering metadata")

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    action_references = re.findall(r"^\s*-\s+uses:\s+([^#\s]+)", workflow, flags=re.MULTILINE)
    if not action_references or any(
        re.fullmatch(r"[^@]+@[0-9a-f]{40}", reference) is None for reference in action_references
    ):
        raise ValueError("GitHub Actions must use immutable full commit SHAs")
    if "scripts.validate_repository_hygiene" not in workflow:
        raise ValueError("CI must enforce the repository hygiene gate")
    if "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" not in workflow:
        raise ValueError("Gitleaks PR scanning must receive the read-only workflow token")


if __name__ == "__main__":
    main()
