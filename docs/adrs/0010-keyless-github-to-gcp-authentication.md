# ADR-0010: Use keyless GitHub-to-Google Cloud authentication

## Status

Accepted.

## Context

Future CI/CD workflows will need to deploy independently scoped services to Google Cloud
and Firebase. A long-lived service-account JSON key stored in a developer machine,
repository, GitHub secret, artifact, or log creates a reusable credential that can
survive the workflow that needed it.

The repository is public, so pull requests and workflow changes are untrusted until
reviewed. Production promotion must also remain an explicit human decision.

## Decision

GitHub Actions will authenticate to Google Cloud with OpenID Connect and Workload
Identity Federation. Long-lived service-account key files are prohibited.

- Each environment uses a dedicated Google Cloud service account with least-privilege
  IAM. Development, staging, production, and execution-plane identities are isolated.
- Workload Identity Provider conditions bind trust to this repository's immutable
  repository identity and to the approved branch or protected GitHub Environment.
- Deployment jobs grant `id-token: write` only at the job that exchanges the token and
  retain `contents: read`; other jobs remain read-only.
- Short-lived credentials are minted only after branch, environment, and approval
  conditions succeed.
- Runtime secrets are referenced from Google Secret Manager or an equivalent managed
  secret binding. Secret values never appear in workflow YAML, Terraform variables,
  App Hosting configuration, command arguments, artifacts, or logs.
- Production deployments remain manual and use a separately protected environment.

## Consequences

Compromising a repository clone or an expired workflow token does not provide a reusable
Google Cloud private key. IAM, provider conditions, and GitHub Environment protection
become required deployment controls and must be reviewed together.

Initial cloud bootstrap requires an administrator to create the identity pool, provider,
service accounts, conditions, and least-privilege roles. Emergency access is handled
outside this repository and must not introduce a service-account key file as a shortcut.

## Alternatives rejected

- **Service-account JSON stored as a GitHub secret:** encrypted storage does not remove
  the long-lived credential, rotation, workflow-exfiltration, or accidental logging risk.
- **Developer credentials used by CI:** not reproducible, attributable, or least
  privilege.
- **One deployment identity for every environment:** increases blast radius and permits
  unintended cross-environment promotion.
