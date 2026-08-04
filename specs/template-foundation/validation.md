# Phase 2 validation record

Validation date: 2026-08-04

## Passed

- `ruff check .` and `ruff format --check .`: passed.
- `mypy gcp/services/control-plane/src scripts`: passed in strict mode (34 files).
- `pytest`: 61 passed, 1 PostgreSQL integration test skipped because no integration URL
  was available; measured statement and branch coverage was 100%.
- `pnpm format:check`, `pnpm lint`, and `pnpm typecheck`: passed.
- `pnpm test:coverage`: 8 tests passed with 100% statements, branches, functions, and
  lines for measured frontend logic.
- `pnpm build`: production Next.js build passed.
- `python scripts/validate_architecture.py`: passed.
- `python -m scripts.validate_repository_hygiene`: passed before independent repository
  initialization; a subsequent direct filesystem scan passed for all 181 source files.
- `python scripts/bootstrap_template.py --config template.config.example.json --check`:
  passed.
- `git diff --check`: passed.
- Residual source-product identity scan: no matches in the working tree; inherited Git
  history and remotes were removed when the independent repository was initialized.
- `pnpm audit`: no known vulnerabilities after applying compatible transitive security
  floors.

## Environment-limited validations

- `pnpm test:firebase`: not executed beyond emulator startup because Java is not
  installed. The failure occurred before the rules test suite started.
- `pnpm test:apphosting`: emulator startup did not complete within 180 seconds and was
  terminated; no application assertion ran.
- `docker compose config` and PostgreSQL RLS integration: Docker is not installed in this
  environment. The PostgreSQL test remains the single documented pytest skip.

These environmental limitations do not replace CI execution on a runner with Java and
Docker. They remain mandatory before the first published release.
