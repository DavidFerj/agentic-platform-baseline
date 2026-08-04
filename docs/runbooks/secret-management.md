# Secret management and leak prevention runbook

## Non-negotiable policy

Never place credentials, private keys, access or refresh tokens, production database
URLs, session data, customer data, or private infrastructure exports inside this
repository. Renaming, encoding, encrypting, or placing a value in a test fixture does not
make it safe to commit.

Firebase web configuration and intentionally public service URLs are not authentication
secrets, but they still belong in environment-specific configuration. Authorization,
Firestore Security Rules, App Check, IAM, quotas, and abuse monitoring must protect the
underlying resources.

## Local development

1. Install the versioned repository hooks once:

   ```text
   uv run python scripts/install_repository_hooks.py
   ```

2. Copy approved example files and store real local values only in ignored files.
3. Keep Google Application Default Credentials outside the checkout. Prefer user ADC for
   local development and never point `GOOGLE_APPLICATION_CREDENTIALS` to a file below the
   repository root.
4. Before committing, verify the intended files:

   ```text
   git status --short
   uv run python -m scripts.validate_repository_hygiene --staged
   ```

5. Before pushing, run:

   ```text
   uv run python -m scripts.validate_repository_hygiene
   ```

The hooks fail closed when Python is unavailable. Do not use `--no-verify` to bypass a
finding. A false positive requires an explicit, reviewed policy change.

## Cloud and CI/CD

- Store runtime secret values in Google Secret Manager and inject references, never
  plaintext values, into Cloud Run, Cloud Functions, or Firebase App Hosting.
- Use the keyless Workload Identity Federation design in
  [ADR-0010](../adrs/0010-keyless-github-to-gcp-authentication.md).
- Separate service identities and secret access by environment and deployable boundary.
- Keep GitHub workflow permissions read-only by default. Grant `id-token: write` only to
  the deployment job that needs short-lived Google credentials.
- Do not print environment dumps, authentication responses, request bodies, headers, or
  resolved deployment configuration to CI logs.
- Treat Terraform state and variable values as private managed artifacts. Use a protected
  remote backend with encryption, locking, access logging, and least-privilege IAM.

## If a secret may have leaked

1. Stop the push or deployment, but do not copy the value into chat, an issue, or a log.
2. Revoke or rotate the credential immediately. Assume compromise even when the commit
   was quickly removed.
3. Preserve only non-sensitive evidence: path, commit, detection time, provider, and
   remediation owner.
4. Report through GitHub private vulnerability reporting as defined in
   [SECURITY.md](../../SECURITY.md).
5. After rotation, remove the material from the working tree and affected Git history.
   Coordinate any history rewrite because all clones and open branches are affected.
6. Re-run the repository hygiene gate, Gitleaks history scan, GitHub secret scanning,
   CodeQL, and dependency/security checks.
7. Document cause, blast radius, rotation evidence, and the preventive control added.

Deleting a file or commit is not remediation by itself; credentials must be revoked or
rotated first.
