from uuid import uuid4

from platform_api.domain.tenancy.entities import MembershipRole, TenantContext
from platform_api.infrastructure.persistence.base import Base
from platform_api.infrastructure.persistence.models import (
    AuditEvent,
    IdentityTenantMapping,
    Membership,
    Project,
    ProjectStatus,
    Tenant,
    User,
    Workspace,
)


def test_tenant_context_checks_any_required_role() -> None:
    context = TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        roles=frozenset({MembershipRole.PRODUCT_OWNER}),
    )

    assert context.has_any_role(MembershipRole.PRODUCT_OWNER, MembershipRole.TENANT_ADMIN)
    assert not context.has_any_role(MembershipRole.VIEWER)


def test_foundation_schema_has_tenant_keys_and_expected_entities() -> None:
    expected_tables = {
        "tenants",
        "users",
        "identity_tenant_mappings",
        "memberships",
        "workspaces",
        "projects",
        "audit_events",
    }

    assert set(Base.metadata.tables) == expected_tables
    for table_name in {"memberships", "workspaces", "projects", "audit_events"}:
        assert Base.metadata.tables[table_name].c.tenant_id.nullable is False

    assert Tenant.__tablename__ == "tenants"
    assert User.__tablename__ == "users"
    assert IdentityTenantMapping.__tablename__ == "identity_tenant_mappings"
    assert Membership.__tablename__ == "memberships"
    assert Workspace.__tablename__ == "workspaces"
    assert Project.__tablename__ == "projects"
    assert AuditEvent.__tablename__ == "audit_events"
    assert ProjectStatus.DRAFT.value == "draft"

    user_constraints = {constraint.name for constraint in User.__table__.constraints}
    workspace_constraints = {constraint.name for constraint in Workspace.__table__.constraints}
    project_constraints = {constraint.name for constraint in Project.__table__.constraints}

    assert "uq_user_external_identity" in user_constraints
    mapping_constraints = {
        constraint.name for constraint in IdentityTenantMapping.__table__.constraints
    }
    assert "uq_identity_tenant_mapping_external" in mapping_constraints
    assert "uq_identity_tenant_mapping_internal" in mapping_constraints
    assert "uq_workspace_tenant_id" in workspace_constraints
    assert "fk_project_tenant_workspace" in project_constraints


def test_initial_migration_forces_rls_for_every_tenant_table() -> None:
    migration_path = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "migrations/versions/0001_foundation_schema.py"
    )
    migration = migration_path.read_text(encoding="utf-8")

    for table_name in ("memberships", "workspaces", "projects", "audit_events"):
        assert table_name in migration
    assert "FORCE ROW LEVEL SECURITY" in migration
    assert "current_setting('app.tenant_id', true)" in migration
    assert "fk_project_tenant_workspace" in migration
    assert "audit_events_tenant_insert" in migration
    assert "audit_events_immutable" in migration
