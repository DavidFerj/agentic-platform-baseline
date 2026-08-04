# Template foundation requirements

## Objective

Deliver a reusable, vertical-neutral software-platform baseline that can be adopted
without inheriting product-specific identity, secrets, infrastructure identifiers, or
business workflow assumptions.

## Functional requirements

- **TPL-REQ-001** — Provide one validated configuration file for project identity.
- **TPL-REQ-002** — Provide a deterministic local bootstrap command that updates the
  documented identity surfaces and Python package boundary.
- **TPL-REQ-003** — Preserve the working Next.js, Python control-plane, Firebase,
  PostgreSQL, contracts, CI, security, and observability foundations.
- **TPL-REQ-004** — Use generic tenant, workspace, project, membership, and audit models.
- **TPL-REQ-005** — Keep provider credentials and environment-specific values outside
  version control.
- **TPL-REQ-006** — Document adoption, validation, provenance, and deferred capabilities.
- **TPL-REQ-007** — Keep AgentOps, multi-agent orchestration, model lifecycle, and
  vertical business logic outside Phase 2.

## Non-functional requirements

- **TPL-NFR-001** — Bootstrap input is allow-listed and identifier formats are validated.
- **TPL-NFR-002** — Tenant isolation, deny-by-default Firebase rules, immutable audit
  evidence, keyless CI/CD guidance, and pinned CI actions remain intact.
- **TPL-NFR-003** — The baseline remains testable locally and reproducible in CI.
- **TPL-NFR-004** — Template adoption must not contact a cloud provider or create a
  remote repository.
