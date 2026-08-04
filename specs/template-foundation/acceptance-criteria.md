# Template foundation acceptance criteria

- **TPL-AC-001** — A complete valid configuration passes bootstrap validation.
- **TPL-AC-002** — Missing, empty, malformed, or unexpected configuration fields fail
  before repository content is changed.
- **TPL-AC-003** — Bootstrap can rename the Python package and replace all documented
  baseline identity tokens.
- **TPL-AC-004** — CODEOWNERS is generated from a non-binding example with the configured
  GitHub owner.
- **TPL-AC-005** — Runtime code and active documentation contain no product-specific
  business workflow or original owner identity.
- **TPL-AC-006** — Architecture and repository-hygiene validation pass.
- **TPL-AC-007** — Frontend and backend lint, type, test, coverage, and build gates pass.
- **TPL-AC-008** — The resulting repository has no publication remote and no secrets.
- **TPL-AC-009** — Deferred AgentOps/MLOps scope is explicit and cannot be mistaken for
  implemented capability.
