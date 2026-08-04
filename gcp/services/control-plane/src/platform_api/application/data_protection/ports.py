"""Ports required by operational data-protection orchestration."""

from typing import Protocol

from platform_api.application.data_protection.models import DecisionAuditRecord, PolicyReference
from platform_api.domain.data_protection import ProtectionPolicy


class PolicyNotFoundError(LookupError):
    """Raised when a server-selected policy version is unavailable."""


class DecisionAuditConflictError(RuntimeError):
    """Raised when an idempotency key is reused for different evidence."""


class PolicyRegistry(Protocol):
    """Resolve an immutable policy from a server-controlled registry."""

    def resolve(self, reference: PolicyReference) -> ProtectionPolicy:
        """Return the exact policy version or fail closed."""
        ...


class DecisionAuditLog(Protocol):
    """Persist decision evidence before a caller may act on it."""

    async def append(self, record: DecisionAuditRecord) -> None:
        """Append idempotently or raise without returning an unaudited decision."""
        ...
