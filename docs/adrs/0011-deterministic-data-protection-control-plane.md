# ADR-0011: Deterministic data-protection control plane

- Status: Accepted
- Date: 2026-08-04

## Context

Projects derived from this baseline may process tenant-scoped product data and later
coordinate agents and model providers. Authorization alone cannot express purpose
limitation, classification, processing authority, provider/region constraints,
retention duties, or human review. Decisions must be inspectable and reproducible. A
language model is not an appropriate final authority for privacy, security, or
compliance decisions.

## Decision

Use a provider-independent, deterministic policy engine in the control-plane domain.
It receives trusted normalized context and one immutable versioned policy, then returns
`permit`, `deny`, or `require_approval`, stable reasons, enforceable obligations, and a
SHA-256 fingerprint over the complete decision input and output. Unknown or mismatched
facts fail closed. Source payloads and credentials are excluded from evidence.

The first implementation remains an internal domain capability. No unauthenticated API
is added. Framework and regulatory entries are reusable inactive templates; a derived
project must perform its own applicability and legal review before activation. Runtime
integrations must store policy decisions through the append-only audit boundary.

## Consequences

- AgentOps, MLOps, APIs, and workflows can reuse one explicit decision contract.
- Callers must enforce returned obligations; a permit is not proof of legal compliance.
- Policy rollout, evidence persistence, consent, retention execution, rights workflows,
  vendor governance, and continuous monitoring remain follow-up work.
- Changing decision semantics or the evidence contract requires a new compatible
  contract or a documented migration.
