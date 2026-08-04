"""SQLAlchemy append-only persistence for policy-decision evidence."""

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from platform_api.application.data_protection.models import DecisionAuditRecord
from platform_api.application.data_protection.ports import DecisionAuditConflictError
from platform_api.infrastructure.persistence.models import AuditEvent

POLICY_DECISION_ACTION = "data_protection.policy_evaluated"


class SqlAlchemyDecisionAuditLog:
    """Store metadata-only decision evidence behind tenant RLS."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def append(self, record: DecisionAuditRecord) -> None:
        """Append once per tenant/request/action and reject conflicting reuse."""
        decision = record.decision
        async with self._session_factory() as session, session.begin():
            await self._set_tenant_context(session, str(decision.tenant_id))
            existing = await session.scalar(
                select(AuditEvent).where(
                    AuditEvent.tenant_id == decision.tenant_id,
                    AuditEvent.action == POLICY_DECISION_ACTION,
                    AuditEvent.request_id == record.request_id,
                )
            )
            if existing is not None:
                fingerprint = existing.payload.get("evidence_fingerprint")
                if fingerprint != decision.evidence_fingerprint:
                    raise DecisionAuditConflictError(
                        "request identifier already records different policy evidence"
                    )
                return
            session.add(
                AuditEvent(
                    tenant_id=decision.tenant_id,
                    actor_id=decision.actor_id,
                    action=POLICY_DECISION_ACTION,
                    resource_type=decision.resource_type,
                    resource_id=decision.resource_id,
                    request_id=record.request_id,
                    payload=record.payload(),
                )
            )

    @staticmethod
    async def _set_tenant_context(session: AsyncSession, tenant_id: str) -> None:
        bind = session.get_bind()
        if bind.dialect.name == "postgresql":
            await session.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant_id},
            )
