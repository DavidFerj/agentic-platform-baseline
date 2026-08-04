"""Framework-independent tenancy identifiers and roles."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class MembershipRole(StrEnum):
    """Baseline tenant roles."""

    TENANT_ADMIN = "tenant_admin"
    PRODUCT_OWNER = "product_owner"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Trusted identity context established after authentication."""

    tenant_id: UUID
    user_id: UUID
    roles: frozenset[MembershipRole]

    def has_any_role(self, *required: MembershipRole) -> bool:
        """Return whether the identity carries at least one required role."""
        return bool(self.roles.intersection(required))
