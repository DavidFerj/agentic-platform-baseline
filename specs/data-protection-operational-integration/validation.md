# Validation evidence

Date: 2026-08-04

| Gate                 | Command / scope                                          | Result           |
| -------------------- | -------------------------------------------------------- | ---------------- |
| Python format        | `uv run ruff format` on changed Python files             | Passed           |
| Python lint          | `uv run ruff check .`                                    | Passed           |
| Python types         | `uv run mypy gcp/services/control-plane/src scripts`     | Passed; 44 files |
| Unit and integration | `uv run pytest` with isolated PostgreSQL 16.4            | Passed; 76 tests |
| Coverage             | pytest statement and branch coverage                     | Passed; 100%     |
| Contracts            | `uv run python scripts/validate_contracts.py`            | Passed           |
| Architecture         | `uv run python scripts/validate_architecture.py`         | Passed           |
| Hygiene              | `uv run python -m scripts.validate_repository_hygiene`   | Passed           |
| Compose definition   | `docker compose config --services` with ephemeral values | Passed           |
| Frontend format      | `pnpm format:check`                                      | Passed           |
| Frontend lint        | `pnpm lint`                                              | Passed           |
| Frontend types       | `pnpm typecheck`                                         | Passed           |
| Frontend tests       | `pnpm test`                                              | Passed; 8 tests  |
| Frontend build       | `pnpm build`                                             | Passed           |

The first Compose-based PostgreSQL attempt timed out because the service does not publish
its port to the Windows host. It was stopped without deleting its volume. The integration
was repeated successfully with a disposable PostgreSQL 16.4 container bound only to
`127.0.0.1:55432`; the container was automatically removed after all 76 tests passed.

This evidence covers the local Phase 3B branch. Remote CI has not been run for the branch
because it has not yet been staged, committed, published, or submitted as a pull request.
