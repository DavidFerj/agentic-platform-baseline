# Adoption guide

1. Start from a clean copy of this repository.
2. Copy `template.config.example.json` to the ignored `template.config.json`.
3. Replace every value with the new project's public, non-secret identity.
4. Run `uv run python scripts/bootstrap_template.py --check`.
5. Run `uv run python scripts/bootstrap_template.py` once.
6. Review the diff, especially package names, contracts, CODEOWNERS, security links, and
   user-facing copy.
7. Install the repository hooks and run the full validation commands in the root README.
8. Create a clean initial commit and remote only after the review succeeds.

The bootstrap does not provision Firebase, Google Cloud, GitHub, databases, secrets, IAM,
or environments. Use separate development, staging, and production projects. Store
credentials in provider secret managers and use Workload Identity Federation for CI/CD.

## Extension sequence

Add a vertical through versioned specifications and contracts first. Add deployable
services only when independent scaling, security, lifecycle, or ownership justifies the
boundary. Preserve tenant isolation and idempotency tests for every new data or event path.

Agent orchestration and MLOps belong to later phases. Their extension points exist, but
their runtime, model registry, evaluation, prompt lifecycle, and governance are not part
of this baseline.
