"""Initial tenant-aware relational model."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from platform_api.domain.tenancy.entities import MembershipRole
from platform_api.infrastructure.persistence.base import Base, TimestampMixin


class ProjectStatus(StrEnum):
    """Generic lifecycle states for a tenant-owned project."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Tenant(TimestampMixin, Base):
    """Customer organization security boundary."""

    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)


class User(TimestampMixin, Base):
    """Platform identity qualified by its trusted external issuer."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "issuer",
            "identity_tenant",
            "subject",
            name="uq_user_external_identity",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    identity_tenant: Mapped[str] = mapped_column(String(128), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)


class IdentityTenantMapping(TimestampMixin, Base):
    """Auditable mapping from an external identity tenant to an internal tenant."""

    __tablename__ = "identity_tenant_mappings"
    __table_args__ = (
        UniqueConstraint(
            "issuer",
            "identity_tenant",
            name="uq_identity_tenant_mapping_external",
        ),
        UniqueConstraint("tenant_id", name="uq_identity_tenant_mapping_internal"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    identity_tenant: Mapped[str] = mapped_column(String(128), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )


class Membership(TimestampMixin, Base):
    """A user's role inside exactly one tenant."""

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),
        Index("ix_memberships_tenant_id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role", native_enum=False),
        nullable=False,
    )


class Workspace(TimestampMixin, Base):
    """Tenant-owned workspace that scopes projects and future executions."""

    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_workspace_tenant_id"),
        UniqueConstraint("tenant_id", "name", name="uq_workspace_tenant_name"),
        Index("ix_workspaces_tenant_id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)


class Project(TimestampMixin, Base):
    """Tenant-owned generic project inside a workspace."""

    __tablename__ = "projects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "workspace_id"],
            ["workspaces.tenant_id", "workspaces.id"],
            name="fk_project_tenant_workspace",
            ondelete="CASCADE",
        ),
        Index("ix_projects_tenant_workspace", "tenant_id", "workspace_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", native_enum=False),
        default=ProjectStatus.DRAFT,
        nullable=False,
    )


class AuditEvent(Base):
    """Append-only evidence for security and traceability."""

    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_events_tenant_occurred", "tenant_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
