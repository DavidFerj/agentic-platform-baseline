"""Make append-only audit requests idempotent.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_audit_event_tenant_action_request",
        "audit_events",
        ["tenant_id", "action", "request_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_audit_event_tenant_action_request",
        "audit_events",
        type_="unique",
    )
