"""Deterministic, fail-closed data-protection policy evaluation."""

import hashlib
import json

from platform_api.domain.data_protection.entities import (
    AuthorityBasis,
    DataClassification,
    DecisionEffect,
    DecisionObligation,
    DecisionReason,
    PolicyContext,
    PolicyDecision,
    ProtectionPolicy,
)

_CLASSIFICATION_RANK = {
    DataClassification.PUBLIC: 0,
    DataClassification.INTERNAL: 1,
    DataClassification.CONFIDENTIAL: 2,
    DataClassification.RESTRICTED: 3,
    DataClassification.REGULATED_HIGH_IMPACT: 4,
}


class DataProtectionPolicyEngine:
    """Evaluate trusted context against one explicit versioned policy."""

    def evaluate(self, context: PolicyContext, policy: ProtectionPolicy) -> PolicyDecision:
        """Return a stable decision and obligations without external side effects."""
        denial_reasons = self._denial_reasons(context, policy)
        obligations: tuple[DecisionObligation, ...]
        if denial_reasons:
            effect = DecisionEffect.DENY
            reasons = tuple(denial_reasons)
            obligations = (DecisionObligation.AUDIT_DECISION,)
        elif context.action in policy.approval_required_actions:
            effect = DecisionEffect.REQUIRE_APPROVAL
            reasons = (DecisionReason.APPROVAL_REQUIRED,)
            obligations = (
                *self._data_obligations(context.classification),
                DecisionObligation.HUMAN_APPROVAL,
            )
        else:
            effect = DecisionEffect.PERMIT
            reasons = (DecisionReason.POLICY_MATCHED,)
            obligations = self._data_obligations(context.classification)

        fingerprint = self._fingerprint(context, policy, effect, reasons, obligations)
        return PolicyDecision(
            tenant_id=context.tenant_id,
            actor_id=context.actor_id,
            resource_type=context.resource_type,
            resource_id=context.resource_id,
            action=context.action,
            purpose=context.purpose,
            effect=effect,
            reasons=reasons,
            obligations=obligations,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            evidence_fingerprint=fingerprint,
        )

    @staticmethod
    def _denial_reasons(context: PolicyContext, policy: ProtectionPolicy) -> list[DecisionReason]:
        reasons: list[DecisionReason] = []
        if context.action not in policy.allowed_actions:
            reasons.append(DecisionReason.ACTION_NOT_ALLOWED)
        if context.purpose not in policy.allowed_purposes:
            reasons.append(DecisionReason.PURPOSE_NOT_ALLOWED)
        if not context.roles.intersection(policy.allowed_roles):
            reasons.append(DecisionReason.ROLE_NOT_ALLOWED)
        if context.authority_basis not in policy.allowed_authority_bases:
            reasons.append(DecisionReason.AUTHORITY_NOT_ALLOWED)
        if context.authority_basis is AuthorityBasis.CONSENT and not context.consent_reference:
            reasons.append(DecisionReason.CONSENT_EVIDENCE_REQUIRED)
        if context.provider is not None and context.provider not in policy.allowed_providers:
            reasons.append(DecisionReason.PROVIDER_NOT_ALLOWED)
        if context.region is not None and context.region not in policy.allowed_regions:
            reasons.append(DecisionReason.REGION_NOT_ALLOWED)
        if (
            _CLASSIFICATION_RANK[context.classification]
            > _CLASSIFICATION_RANK[policy.maximum_classification]
        ):
            reasons.append(DecisionReason.CLASSIFICATION_NOT_ALLOWED)
        return reasons

    @staticmethod
    def _data_obligations(
        classification: DataClassification,
    ) -> tuple[DecisionObligation, ...]:
        obligations = [
            DecisionObligation.AUDIT_DECISION,
            DecisionObligation.ENFORCE_RETENTION,
        ]
        if (
            _CLASSIFICATION_RANK[classification]
            >= _CLASSIFICATION_RANK[DataClassification.CONFIDENTIAL]
        ):
            obligations.append(DecisionObligation.MINIMIZE_DATA)
        if (
            _CLASSIFICATION_RANK[classification]
            >= _CLASSIFICATION_RANK[DataClassification.RESTRICTED]
        ):
            obligations.append(DecisionObligation.REDACT_DIRECT_IDENTIFIERS)
        return tuple(obligations)

    @staticmethod
    def _fingerprint(
        context: PolicyContext,
        policy: ProtectionPolicy,
        effect: DecisionEffect,
        reasons: tuple[DecisionReason, ...],
        obligations: tuple[DecisionObligation, ...],
    ) -> str:
        evidence = {
            "context": {
                "tenant_id": str(context.tenant_id),
                "actor_id": str(context.actor_id),
                "roles": sorted(context.roles),
                "action": context.action,
                "resource_type": context.resource_type,
                "resource_id": context.resource_id,
                "purpose": context.purpose,
                "classification": context.classification,
                "authority_basis": context.authority_basis,
                "provider": context.provider,
                "region": context.region,
                "consent_reference": context.consent_reference,
            },
            "policy": {
                "policy_id": policy.policy_id,
                "version": policy.version,
                "allowed_actions": sorted(policy.allowed_actions),
                "allowed_purposes": sorted(policy.allowed_purposes),
                "allowed_roles": sorted(policy.allowed_roles),
                "allowed_authority_bases": sorted(policy.allowed_authority_bases),
                "allowed_providers": sorted(policy.allowed_providers),
                "allowed_regions": sorted(policy.allowed_regions),
                "maximum_classification": policy.maximum_classification,
                "approval_required_actions": sorted(policy.approval_required_actions),
            },
            "decision": {
                "effect": effect,
                "reasons": reasons,
                "obligations": obligations,
            },
        }
        canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"
