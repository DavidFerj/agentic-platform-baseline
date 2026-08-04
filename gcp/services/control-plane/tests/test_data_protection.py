import json
from dataclasses import asdict, replace
from pathlib import Path
from uuid import UUID

import pytest
from jsonschema import Draft202012Validator
from yaml import safe_load

from platform_api.domain.data_protection import (
    AuthorityBasis,
    DataClassification,
    DataProtectionPolicyEngine,
    DecisionEffect,
    DecisionObligation,
    DecisionReason,
    PolicyContext,
    ProtectionPolicy,
)

ROOT = Path(__file__).resolve().parents[4]


def make_policy(**changes: object) -> ProtectionPolicy:
    policy = ProtectionPolicy(
        policy_id="platform-default",
        version="1.0.0",
        allowed_actions=frozenset({"read", "export", "delete"}),
        allowed_purposes=frozenset({"deliver_platform"}),
        allowed_roles=frozenset({"tenant_admin", "contributor"}),
        allowed_authority_bases=frozenset({AuthorityBasis.CONTRACT, AuthorityBasis.CONSENT}),
        allowed_providers=frozenset({"approved-provider"}),
        allowed_regions=frozenset({"us-east1"}),
        maximum_classification=DataClassification.RESTRICTED,
        approval_required_actions=frozenset({"export", "delete"}),
    )
    return replace(policy, **changes)


def make_context(**changes: object) -> PolicyContext:
    context = PolicyContext(
        tenant_id=UUID("35ec55a5-1abc-4cd8-8c29-e58b391641c6"),
        actor_id=UUID("a3816945-4240-4c42-a1ae-45124bd315f1"),
        roles=frozenset({"contributor"}),
        action="read",
        resource_type="delivery_specification",
        resource_id="specification-123",
        purpose="deliver_platform",
        classification=DataClassification.INTERNAL,
        authority_basis=AuthorityBasis.CONTRACT,
    )
    return replace(context, **changes)


@pytest.mark.parametrize(
    ("classification", "expected"),
    [
        (
            DataClassification.PUBLIC,
            (
                DecisionObligation.AUDIT_DECISION,
                DecisionObligation.ENFORCE_RETENTION,
            ),
        ),
        (
            DataClassification.CONFIDENTIAL,
            (
                DecisionObligation.AUDIT_DECISION,
                DecisionObligation.ENFORCE_RETENTION,
                DecisionObligation.MINIMIZE_DATA,
            ),
        ),
        (
            DataClassification.RESTRICTED,
            (
                DecisionObligation.AUDIT_DECISION,
                DecisionObligation.ENFORCE_RETENTION,
                DecisionObligation.MINIMIZE_DATA,
                DecisionObligation.REDACT_DIRECT_IDENTIFIERS,
            ),
        ),
    ],
)
def test_permit_returns_classification_obligations(
    classification: DataClassification,
    expected: tuple[DecisionObligation, ...],
) -> None:
    decision = DataProtectionPolicyEngine().evaluate(
        make_context(classification=classification), make_policy()
    )

    assert decision.effect is DecisionEffect.PERMIT
    assert decision.reasons == (DecisionReason.POLICY_MATCHED,)
    assert decision.obligations == expected
    assert decision.evidence_fingerprint.startswith("sha256:")


def test_high_impact_action_requires_human_approval() -> None:
    decision = DataProtectionPolicyEngine().evaluate(
        make_context(action="export", classification=DataClassification.CONFIDENTIAL),
        make_policy(),
    )

    assert decision.effect is DecisionEffect.REQUIRE_APPROVAL
    assert decision.reasons == (DecisionReason.APPROVAL_REQUIRED,)
    assert decision.obligations[-1] is DecisionObligation.HUMAN_APPROVAL


def test_all_policy_mismatches_are_reported_and_fail_closed() -> None:
    context = make_context(
        roles=frozenset({"viewer"}),
        action="unknown",
        purpose="unapproved",
        classification=DataClassification.REGULATED_HIGH_IMPACT,
        authority_basis=AuthorityBasis.NONE,
        provider="unknown-provider",
        region="europe-west1",
    )

    decision = DataProtectionPolicyEngine().evaluate(context, make_policy())

    assert decision.effect is DecisionEffect.DENY
    assert decision.reasons == (
        DecisionReason.ACTION_NOT_ALLOWED,
        DecisionReason.PURPOSE_NOT_ALLOWED,
        DecisionReason.ROLE_NOT_ALLOWED,
        DecisionReason.AUTHORITY_NOT_ALLOWED,
        DecisionReason.PROVIDER_NOT_ALLOWED,
        DecisionReason.REGION_NOT_ALLOWED,
        DecisionReason.CLASSIFICATION_NOT_ALLOWED,
    )
    assert decision.obligations == (DecisionObligation.AUDIT_DECISION,)


def test_consent_requires_a_nonempty_evidence_reference() -> None:
    denied = DataProtectionPolicyEngine().evaluate(
        make_context(authority_basis=AuthorityBasis.CONSENT), make_policy()
    )
    permitted = DataProtectionPolicyEngine().evaluate(
        make_context(
            authority_basis=AuthorityBasis.CONSENT,
            consent_reference="consent-record-123",
        ),
        make_policy(),
    )

    assert denied.reasons == (DecisionReason.CONSENT_EVIDENCE_REQUIRED,)
    assert permitted.effect is DecisionEffect.PERMIT


def test_fingerprint_is_reproducible_and_input_sensitive() -> None:
    engine = DataProtectionPolicyEngine()
    context = make_context(roles=frozenset({"contributor", "tenant_admin"}))

    first = engine.evaluate(context, make_policy())
    reordered = engine.evaluate(
        replace(context, roles=frozenset({"tenant_admin", "contributor"})), make_policy()
    )
    changed = engine.evaluate(replace(context, resource_id="specification-456"), make_policy())

    assert first.evidence_fingerprint == reordered.evidence_fingerprint
    assert first.evidence_fingerprint != changed.evidence_fingerprint


def test_decision_contract_accepts_engine_evidence() -> None:
    schema_path = ROOT / "gcp/packages/contracts/compliance/policy-decision.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    decision = DataProtectionPolicyEngine().evaluate(make_context(), make_policy())
    evidence = json.loads(json.dumps(asdict(decision), default=str))

    Draft202012Validator(schema).validate(evidence)
    assert schema["additionalProperties"] is False


def test_governance_registries_are_versioned_and_overlays_fail_closed() -> None:
    catalog = safe_load((ROOT / "docs/compliance/control-catalog.yaml").read_text(encoding="utf-8"))
    matrix = safe_load(
        (ROOT / "docs/compliance/applicability-matrix.yaml").read_text(encoding="utf-8")
    )
    inventory = safe_load(
        (ROOT / "docs/compliance/data-inventory.yaml").read_text(encoding="utf-8")
    )

    assert catalog["schema_version"] == 1
    assert len({control["id"] for control in catalog["controls"]}) == len(catalog["controls"])
    assert matrix["schema_version"] == 1
    assert all(
        overlay["enforcement_enabled"] is False
        for overlay in matrix["legal_and_assurance_overlays"]
    )
    assert inventory["inventory_id"] == "platform-baseline-processing-activities"
    assert all(
        activity["external_providers"] == [] for activity in inventory["processing_activities"]
    )
