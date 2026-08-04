"""Authenticated orchestration for deterministic data-protection decisions."""

from collections.abc import Callable
from datetime import UTC, datetime

from platform_api.application.data_protection.models import (
    DecisionAuditRecord,
    PolicyReference,
    ProcessingOperation,
)
from platform_api.application.data_protection.ports import DecisionAuditLog, PolicyRegistry
from platform_api.domain.data_protection import (
    DataProtectionPolicyEngine,
    PolicyContext,
    PolicyDecision,
)
from platform_api.domain.tenancy.entities import TenantContext


class DecisionAuditUnavailableError(RuntimeError):
    """Raised when mandatory evidence cannot be durably recorded."""


class DataProtectionControlPlane:
    """Build trusted context, evaluate policy, and persist evidence fail-closed."""

    def __init__(
        self,
        registry: PolicyRegistry,
        audit_log: DecisionAuditLog,
        *,
        engine: DataProtectionPolicyEngine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._audit_log = audit_log
        self._engine = engine or DataProtectionPolicyEngine()
        self._clock = clock or (lambda: datetime.now(UTC))

    async def evaluate(
        self,
        identity: TenantContext,
        operation: ProcessingOperation,
        policy_reference: PolicyReference,
        *,
        request_id: str,
    ) -> PolicyDecision:
        """Return a decision only after its metadata-only evidence is recorded."""
        policy = self._registry.resolve(policy_reference)
        context = PolicyContext(
            tenant_id=identity.tenant_id,
            actor_id=identity.user_id,
            roles=frozenset(role.value for role in identity.roles),
            action=operation.action,
            resource_type=operation.resource_type,
            resource_id=operation.resource_id,
            purpose=operation.purpose,
            classification=operation.classification,
            authority_basis=operation.authority_basis,
            provider=operation.provider,
            region=operation.region,
            consent_reference=operation.consent_reference,
        )
        decision = self._engine.evaluate(context, policy)
        record = DecisionAuditRecord(
            request_id=request_id,
            evaluated_at=self._clock(),
            decision=decision,
        )
        try:
            await self._audit_log.append(record)
        except Exception as exc:
            raise DecisionAuditUnavailableError(
                "data-protection decision evidence could not be recorded"
            ) from exc
        return decision
