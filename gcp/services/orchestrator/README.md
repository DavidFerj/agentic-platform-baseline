# Orchestrator boundary

The orchestrator is intentionally not implemented in Phase 0.

Its future responsibility is durable agent-task lifecycle, checkpoints, budgets,
interruptions, approval gates, provider routing, and evidence consolidation. It will
consume application contracts from the control plane and must not become the owner of
tenant, product, specification, repository, or billing rules.

## Boundary rules

- The control plane authorizes a task before orchestration.
- Every task has stable IDs, allowed paths/tools, forbidden actions, limits, and gates.
- Provider adapters translate an internal contract; product logic never imports a
  provider SDK.
- Coding occurs in an ephemeral workspace derived from a known commit.
- The execution identity cannot read production secrets or promote production releases.
- Egress is denied by default and explicitly allowlisted.
- Logs, diffs, artifacts, and tool-call evidence are preserved before runner teardown.
- The change generator is not the only reviewer.

See ADR-0003 and the threat model before implementing this service.
