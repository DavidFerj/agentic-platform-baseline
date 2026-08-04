"""Provider-independent data-protection policy entities."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class DataClassification(StrEnum):
    """Increasing data sensitivity levels used by the policy engine."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    REGULATED_HIGH_IMPACT = "regulated_high_impact"


class AuthorityBasis(StrEnum):
    """Recorded authority for a processing operation; not a legal determination."""

    CONTRACT = "contract"
    CONSENT = "consent"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_OPERATION = "legitimate_operation"
    PERMITTED_HEALTHCARE = "permitted_healthcare"
    NONE = "none"


class DecisionEffect(StrEnum):
    """Fail-closed outcome returned by policy evaluation."""

    PERMIT = "permit"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class DecisionObligation(StrEnum):
    """Controls that a caller must enforce after a non-denied decision."""

    AUDIT_DECISION = "audit_decision"
    ENFORCE_RETENTION = "enforce_retention"
    MINIMIZE_DATA = "minimize_data"
    REDACT_DIRECT_IDENTIFIERS = "redact_direct_identifiers"
    HUMAN_APPROVAL = "human_approval"


class DecisionReason(StrEnum):
    """Stable machine-readable decision reasons."""

    POLICY_MATCHED = "policy_matched"
    APPROVAL_REQUIRED = "approval_required"
    ACTION_NOT_ALLOWED = "action_not_allowed"
    PURPOSE_NOT_ALLOWED = "purpose_not_allowed"
    ROLE_NOT_ALLOWED = "role_not_allowed"
    AUTHORITY_NOT_ALLOWED = "authority_not_allowed"
    CONSENT_EVIDENCE_REQUIRED = "consent_evidence_required"
    PROVIDER_NOT_ALLOWED = "provider_not_allowed"
    REGION_NOT_ALLOWED = "region_not_allowed"
    CLASSIFICATION_NOT_ALLOWED = "classification_not_allowed"


@dataclass(frozen=True, slots=True)
class PolicyContext:
    """Trusted, normalized facts supplied to a policy evaluation."""

    tenant_id: UUID
    actor_id: UUID
    roles: frozenset[str]
    action: str
    resource_type: str
    resource_id: str
    purpose: str
    classification: DataClassification
    authority_basis: AuthorityBasis
    provider: str | None = None
    region: str | None = None
    consent_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ProtectionPolicy:
    """Immutable, versioned policy consumed by the deterministic engine."""

    policy_id: str
    version: str
    allowed_actions: frozenset[str]
    allowed_purposes: frozenset[str]
    allowed_roles: frozenset[str]
    allowed_authority_bases: frozenset[AuthorityBasis]
    allowed_providers: frozenset[str]
    allowed_regions: frozenset[str]
    maximum_classification: DataClassification
    approval_required_actions: frozenset[str]


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """Auditable policy outcome without source payloads or secrets."""

    tenant_id: UUID
    actor_id: UUID
    resource_type: str
    resource_id: str
    action: str
    purpose: str
    effect: DecisionEffect
    reasons: tuple[DecisionReason, ...]
    obligations: tuple[DecisionObligation, ...]
    policy_id: str
    policy_version: str
    evidence_fingerprint: str
