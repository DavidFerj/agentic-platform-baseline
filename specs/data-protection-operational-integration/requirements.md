# Data-protection operational integration requirements

Status: Approved for baseline implementation
Scope: Phase 3B, slice 1 - trusted orchestration and append-only evidence

## Functional requirements

- **DPOI-REQ-001 - Trusted identity:** tenant, actor, and roles come exclusively from an
  authenticated `TenantContext`; declared operation data cannot override them.
- **DPOI-REQ-002 - Policy resolution:** an exact immutable policy identifier and version
  are resolved from a server-controlled registry; missing versions fail closed.
- **DPOI-REQ-003 - Audited evaluation:** every outcome is appended to the tenant-scoped
  audit boundary before it is returned.
- **DPOI-REQ-004 - Idempotent evidence:** tenant, event action, and request identifier
  form the idempotency key; identical replay does not duplicate and conflicting reuse
  fails closed.
- **DPOI-REQ-005 - Metadata only:** evidence excludes source content, prompts, tokens,
  credentials, and unrestricted payloads.

Audit failure blocks use of a decision. PostgreSQL writes establish transaction-local
tenant context before RLS access. The migration is reversible.

Public APIs, Firebase/OIDC verification, policy UI, approval workflows, obligation
execution, and regulatory activation are outside this slice.
