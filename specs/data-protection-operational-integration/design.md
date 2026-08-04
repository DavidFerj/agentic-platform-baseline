# Design

```text
verified identity -> TenantContext --------+
declared facts -> ProcessingOperation ------+-> DataProtectionControlPlane
server policy -> StaticPolicyRegistry ------+       | deterministic evaluation
                                                       | append before return
                                                       v
                                      SqlAlchemyDecisionAuditLog
                                                       |
                                      PostgreSQL RLS + immutable audit
```

Callers cannot place tenant, actor, or roles in `ProcessingOperation`. Registry lookup
uses an exact version and never falls back. The audit adapter establishes transaction-
local tenant context, accepts an identical retry, and rejects a different fingerprint
for the same tenant/action/request key. A database uniqueness constraint closes the
persistent idempotency boundary.

Evaluation time and request identity belong to the audit envelope, not the deterministic
decision fingerprint. No route is added until verified identity and membership establish
`TenantContext`.
