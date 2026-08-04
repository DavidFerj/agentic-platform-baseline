from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from platform_api.application.data_protection import (
    DataProtectionControlPlane,
    DecisionAuditConflictError,
    DecisionAuditRecord,
    DecisionAuditUnavailableError,
    PolicyNotFoundError,
    PolicyReference,
    ProcessingOperation,
)
from platform_api.domain.data_protection import (
    AuthorityBasis,
    DataClassification,
    DataProtectionPolicyEngine,
    DecisionEffect,
    PolicyContext,
    PolicyDecision,
    ProtectionPolicy,
)
from platform_api.domain.tenancy.entities import MembershipRole, TenantContext
from platform_api.infrastructure.persistence.base import Base
from platform_api.infrastructure.persistence.data_protection import (
    POLICY_DECISION_ACTION,
    SqlAlchemyDecisionAuditLog,
)
from platform_api.infrastructure.persistence.models import AuditEvent, Tenant, User
from platform_api.infrastructure.policy_registry import StaticPolicyRegistry

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)


def _policy() -> ProtectionPolicy:
    return ProtectionPolicy(
        policy_id="baseline-processing",
        version="1.0.0",
        allowed_actions=frozenset({"project.read"}),
        allowed_purposes=frozenset({"product_delivery"}),
        allowed_roles=frozenset({"product_owner"}),
        allowed_authority_bases=frozenset({AuthorityBasis.CONTRACT}),
        allowed_providers=frozenset(),
        allowed_regions=frozenset(),
        maximum_classification=DataClassification.CONFIDENTIAL,
        approval_required_actions=frozenset(),
    )


def _identity() -> TenantContext:
    return TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        roles=frozenset({MembershipRole.PRODUCT_OWNER}),
    )


def _operation() -> ProcessingOperation:
    return ProcessingOperation(
        action="project.read",
        resource_type="project",
        resource_id="project-123",
        purpose="product_delivery",
        classification=DataClassification.CONFIDENTIAL,
        authority_basis=AuthorityBasis.CONTRACT,
    )


def _decision(identity: TenantContext | None = None) -> PolicyDecision:
    trusted = identity or _identity()
    return DataProtectionPolicyEngine().evaluate(
        PolicyContext(
            tenant_id=trusted.tenant_id,
            actor_id=trusted.user_id,
            roles=frozenset(role.value for role in trusted.roles),
            action="project.read",
            resource_type="project",
            resource_id="project-123",
            purpose="product_delivery",
            classification=DataClassification.CONFIDENTIAL,
            authority_basis=AuthorityBasis.CONTRACT,
        ),
        _policy(),
    )


class RecordingAuditLog:
    def __init__(self, error: Exception | None = None) -> None:
        self.records: list[DecisionAuditRecord] = []
        self.error = error

    async def append(self, record: DecisionAuditRecord) -> None:
        if self.error is not None:
            raise self.error
        self.records.append(record)


@pytest.mark.asyncio
async def test_control_plane_uses_trusted_identity_and_audits_before_returning() -> None:
    identity = _identity()
    audit_log = RecordingAuditLog()
    control_plane = DataProtectionControlPlane(
        StaticPolicyRegistry([_policy()]),
        audit_log,
        clock=lambda: NOW,
    )

    decision = await control_plane.evaluate(
        identity,
        _operation(),
        PolicyReference("baseline-processing", "1.0.0"),
        request_id="request-123",
    )

    assert decision.effect is DecisionEffect.PERMIT
    assert decision.tenant_id == identity.tenant_id
    assert decision.actor_id == identity.user_id
    assert len(audit_log.records) == 1
    record = audit_log.records[0]
    assert record.request_id == "request-123"
    assert record.evaluated_at == NOW
    assert record.payload() == {
        "schema_version": "policy-decision.v1",
        "evaluated_at": "2026-08-04T12:00:00+00:00",
        "effect": "permit",
        "reasons": ["policy_matched"],
        "obligations": ["audit_decision", "enforce_retention", "minimize_data"],
        "policy_id": "baseline-processing",
        "policy_version": "1.0.0",
        "purpose": "product_delivery",
        "evidence_fingerprint": decision.evidence_fingerprint,
    }


@pytest.mark.asyncio
async def test_control_plane_fails_closed_when_audit_is_unavailable() -> None:
    control_plane = DataProtectionControlPlane(
        StaticPolicyRegistry([_policy()]),
        RecordingAuditLog(OSError("database unavailable")),
        engine=DataProtectionPolicyEngine(),
    )

    with pytest.raises(DecisionAuditUnavailableError) as error:
        await control_plane.evaluate(
            _identity(),
            _operation(),
            PolicyReference("baseline-processing", "1.0.0"),
            request_id="request-failed",
        )

    assert isinstance(error.value.__cause__, OSError)


def test_static_registry_rejects_duplicates_and_unknown_versions() -> None:
    policy = _policy()
    with pytest.raises(ValueError, match="duplicate policy version"):
        StaticPolicyRegistry([policy, policy])

    registry = StaticPolicyRegistry([policy])
    assert registry.resolve(PolicyReference(policy.policy_id, policy.version)) is policy
    with pytest.raises(PolicyNotFoundError, match="policy version unavailable"):
        registry.resolve(PolicyReference(policy.policy_id, "2.0.0"))


@pytest.mark.asyncio
async def test_sqlalchemy_audit_log_is_idempotent_and_detects_conflicts() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    identity = _identity()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with session_factory.begin() as session:
        session.add(Tenant(id=identity.tenant_id, slug="tenant", display_name="Tenant"))
        session.add(
            User(
                id=identity.user_id,
                issuer="issuer",
                identity_tenant="identity-tenant",
                subject="subject",
                email="user@example.invalid",
            )
        )

    record = DecisionAuditRecord("request-123", NOW, _decision(identity))
    audit_log = SqlAlchemyDecisionAuditLog(session_factory)
    await audit_log.append(record)
    await audit_log.append(record)

    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(AuditEvent))
        stored = await session.scalar(select(AuditEvent))
    assert count == 1
    assert stored is not None
    assert stored.action == POLICY_DECISION_ACTION
    assert stored.payload["evidence_fingerprint"] == record.decision.evidence_fingerprint

    conflict = replace(
        record,
        decision=replace(record.decision, evidence_fingerprint="sha256:different"),
    )
    with pytest.raises(DecisionAuditConflictError):
        await audit_log.append(conflict)
    await engine.dispose()


@pytest.mark.asyncio
async def test_postgres_tenant_context_uses_transaction_local_setting() -> None:
    calls: list[tuple[object, object]] = []

    class FakeSession:
        def get_bind(self):  # type: ignore[no-untyped-def]
            return SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        async def execute(self, statement: object, parameters: object) -> None:
            calls.append((statement, parameters))

    await SqlAlchemyDecisionAuditLog._set_tenant_context(
        cast(AsyncSession, FakeSession()),
        "tenant-123",
    )

    assert len(calls) == 1
    assert calls[0][1] == {"tenant_id": "tenant-123"}
