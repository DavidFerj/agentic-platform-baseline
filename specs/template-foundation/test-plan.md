# Template foundation test plan

| Concern                 | Validation                                                       |
| ----------------------- | ---------------------------------------------------------------- |
| Bootstrap schema        | Unit tests for valid, missing, empty, and malformed values       |
| Identity transformation | Unit test for package rename, token replacement, and CODEOWNERS  |
| Python quality          | Ruff formatting/lint, strict mypy, pytest with branch coverage   |
| Web quality             | ESLint, TypeScript, Vitest coverage, production build            |
| Contracts               | OpenAPI and JSON Schema validator tests                          |
| Architecture            | `scripts/validate_architecture.py`                               |
| Secret hygiene          | repository hygiene validator plus history/worktree scans         |
| Firebase boundary       | Firestore emulator rules tests when Java is available            |
| Containers              | Compose configuration and service tests when Docker is available |

Failures caused by unavailable local services must be recorded as environmental blockers,
never represented as successful validation.
