# Data protection foundation test plan

## Automated behavior

- Parameterize public, confidential, and restricted permitted processing to verify
  retention, minimization, and redaction obligations.
- Verify configured high-impact actions return `require_approval`.
- Combine action, purpose, role, authority, provider, region, and classification failures
  to verify stable aggregation and fail-closed behavior.
- Verify consent without an evidence reference is denied and referenced consent permits.
- Verify fingerprint independence from set order and sensitivity to material input.
- Validate engine output against Draft 2020-12 JSON Schema.
- Parse governance YAML, require unique control IDs, and assert every legal/assurance
  overlay is enforcement-disabled.

## Quality and security gates

Run Ruff formatting/lint, strict mypy, pytest with 100% statement/branch coverage,
architecture validation, repository hygiene, and secret scanning. The full monorepo gate
also includes frontend, Firebase, build, and container checks, although those components
are unchanged by Phase 3A.

## Deferred integration tests

Authenticated API authorization, policy persistence, audit writes, obligation execution,
retention/deletion, and live cloud IAM require later runtime integrations and are not
represented as completed tests.
