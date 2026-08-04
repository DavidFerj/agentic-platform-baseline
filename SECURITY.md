# Security policy

## Reporting

Do not open a public issue for a suspected vulnerability or exposed secret. After
bootstrapping the template, use the repository's private security-advisory link with the
affected component, impact, reproduction steps, and any suggested mitigation.

If private reporting is unavailable, stop work, preserve evidence without copying
sensitive data, and contact the repository owner through their verified GitHub profile.
Do not send credentials, customer code, or production data.

## Supported versions

Security fixes are applied to the latest commit on `main`. Pre-release work on `develop`
is supported only until it is superseded or promoted. No tagged stable release exists
yet.

We aim to acknowledge a complete report within three business days. Validation and
remediation timelines depend on severity and reproducibility. Reporters should allow a
coordinated remediation window before disclosure.

## Baseline controls

- No production secrets, credentials, personal data, or customer code in this repository.
- Versioned pre-commit and pre-push hooks reject sensitive paths and high-confidence
  credential patterns before content reaches GitHub.
- `.gitignore`, `.dockerignore`, and `.gcloudignore` independently exclude local secrets,
  provider credentials, Terraform state, deployment state, database exports, and keys.
- Tenant context comes from validated identity, never from an untrusted request parameter.
- Firebase Authentication establishes identity; application authorization and tenant
  membership remain control-plane responsibilities.
- Firestore client writes are denied by default. Server SDKs use per-service IAM and
  never service-account key files.
- App Check is an anti-abuse signal and never replaces authentication or authorization.
- Production rejects development-header authentication.
- Agent execution uses separate ephemeral identities and isolated workspaces.
- Pull requests require deterministic tests and security scanning before promotion.
- Production deployment is never automatic.
- GitHub Actions dependencies are pinned to immutable commit SHAs.
- GitHub Actions permits only GitHub-owned actions and an explicit provider allowlist;
  repository policy also requires full-length SHA pinning.
- Google Cloud CI/CD uses short-lived Workload Identity Federation. Long-lived
  service-account JSON keys are prohibited.
- Confirmed secrets and unwaived critical/high dependency findings block publication.

See [the secret-management runbook](docs/runbooks/secret-management.md) for prevention
and response, and `specs/template-foundation/threat-model.md` for the initial threat
analysis.
