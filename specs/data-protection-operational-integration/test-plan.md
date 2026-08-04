# Test plan

| Requirement  | Verification                                                       |
| ------------ | ------------------------------------------------------------------ |
| DPOI-REQ-001 | Assert decision tenant and actor match trusted context.            |
| DPOI-REQ-002 | Test exact resolution, duplicate policy, and unknown version.      |
| DPOI-REQ-003 | Test successful append and fail-closed audit failure.              |
| DPOI-REQ-004 | Test identical replay, conflicting fingerprint, and DB uniqueness. |
| DPOI-REQ-005 | Assert the complete metadata-only payload.                         |

Ruff, mypy, full pytest coverage, architecture, hygiene, migration, and PostgreSQL RLS
checks are release gates.
