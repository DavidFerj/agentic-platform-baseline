# ADR-0001: Start the control plane as a modular monolith

Status: Accepted
Date: 2026-07-29

## Context

Derived products can span tenancy, domain workflows, specifications, execution, quality,
repositories, delivery, and usage. Splitting these domains into independently deployed
services before their transaction and scaling boundaries are known would increase local,
operational, and consistency cost.

## Decision

Implement the initial control plane as a FastAPI modular monolith. Keep domain,
application, transport, and infrastructure dependencies explicit. Run agent code in a
separate execution plane even during the MVP.

## Consequences

- Local development, transactions, policy enforcement, and deployment remain simple.
- Modules can be tested without network boundaries.
- Extraction requires evidence such as independent scaling, security isolation,
  ownership, or lifecycle—not file size or theoretical reuse.
- The execution plane remains separately deployable because untrusted code is a genuine
  security boundary.
