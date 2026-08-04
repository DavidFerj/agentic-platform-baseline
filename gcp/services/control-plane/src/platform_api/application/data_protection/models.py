"""Application-level data-protection commands and audit records."""

from dataclasses import dataclass
from datetime import datetime

from platform_api.domain.data_protection import AuthorityBasis, DataClassification, PolicyDecision


@dataclass(frozen=True, slots=True)
class PolicyReference:
    """Server-selected immutable policy identity."""

    policy_id: str
    version: str


@dataclass(frozen=True, slots=True)
class ProcessingOperation:
    """Declared processing facts that cannot override trusted identity context."""

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
class DecisionAuditRecord:
    """Metadata-only append-only evidence for one evaluated request."""

    request_id: str
    evaluated_at: datetime
    decision: PolicyDecision

    def payload(self) -> dict[str, object]:
        """Return JSON-safe evidence without source content or credentials."""
        return {
            "schema_version": "policy-decision.v1",
            "evaluated_at": self.evaluated_at.isoformat(),
            "effect": self.decision.effect.value,
            "reasons": [reason.value for reason in self.decision.reasons],
            "obligations": [obligation.value for obligation in self.decision.obligations],
            "policy_id": self.decision.policy_id,
            "policy_version": self.decision.policy_version,
            "purpose": self.decision.purpose,
            "evidence_fingerprint": self.decision.evidence_fingerprint,
        }
