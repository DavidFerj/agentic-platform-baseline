"""Server-controlled immutable data-protection policy registry."""

from collections.abc import Iterable

from platform_api.application.data_protection.models import PolicyReference
from platform_api.application.data_protection.ports import PolicyNotFoundError
from platform_api.domain.data_protection import ProtectionPolicy


class StaticPolicyRegistry:
    """Resolve explicitly provisioned policy versions without provider calls."""

    def __init__(self, policies: Iterable[ProtectionPolicy]) -> None:
        self._policies: dict[tuple[str, str], ProtectionPolicy] = {}
        for policy in policies:
            key = (policy.policy_id, policy.version)
            if key in self._policies:
                raise ValueError(f"duplicate policy version: {policy.policy_id}@{policy.version}")
            self._policies[key] = policy

    def resolve(self, reference: PolicyReference) -> ProtectionPolicy:
        """Return the exact version or fail closed without fallback."""
        try:
            return self._policies[(reference.policy_id, reference.version)]
        except KeyError as exc:
            raise PolicyNotFoundError(
                f"policy version unavailable: {reference.policy_id}@{reference.version}"
            ) from exc
