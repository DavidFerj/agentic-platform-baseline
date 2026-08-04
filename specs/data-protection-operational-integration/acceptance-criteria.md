# Acceptance criteria

- **DPOI-AC-001:** decision tenant and actor originate from trusted identity. Completed.
- **DPOI-AC-002:** unknown policy versions fail closed. Completed.
- **DPOI-AC-003:** audit failure prevents a decision from being returned. Completed.
- **DPOI-AC-004:** identical retries create one event; conflicting retries fail. Completed.
- **DPOI-AC-005:** persisted evidence contains only approved metadata. Completed.
- **DPOI-AC-006:** RLS tenant context is transaction-local and idempotency is unique in
  the database. Completed.
- **DPOI-AC-007:** no unauthenticated policy endpoint exists. Completed.
