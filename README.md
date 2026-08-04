# Agentic Platform Baseline

A reusable, provider-neutral foundation for building secure multi-tenant agentic
products on Google Cloud. The baseline supplies engineering controls, deployment
boundaries, and executable reference behavior without imposing a vertical-specific
domain.

## Included foundation

- Next.js and strict TypeScript product shell prepared for Firebase App Hosting;
- moderately modular FastAPI control plane for Cloud Run;
- Firebase Authentication, Firestore rules, indexes, and emulator boundaries;
- tenant, identity, membership, workspace, project, and append-only audit models;
- PostgreSQL migrations with forced Row-Level Security;
- versioned HTTP and event contracts with idempotency metadata;
- Docker Compose development stack with PostgreSQL, Redis, MinIO, and OpenTelemetry;
- repository hygiene hooks, dependency review, secret scanning, CodeQL, and CI;
- spec-driven requirements, acceptance criteria, threat analysis, and traceability;
- a deterministic, versioned data-protection decision engine with policy evidence,
  inactive overlay templates, a control catalog, and a processing-inventory extension point.

Agent orchestration and model lifecycle management are deliberate extension points. They
are not presented as implemented capabilities in this baseline and belong to later
AgentOps and MLOps phases. The data-protection foundation supplies technical controls;
it does not activate laws, certify compliance, or replace derived-project legal review.

## Repository map

```text
frontend/               Next.js application and App Hosting configuration
gcp/
  services/             Cohesive Cloud Run HTTP services
  functions/            Narrow idempotent HTTP or CloudEvent adapters
  jobs/                 Finite migrations and isolated execution tasks
  packages/contracts/   Public API and event contracts
  firebase/             Rules, indexes, emulator tests, and BaaS policy
  infrastructure/       Containers, observability, and Terraform boundary
specs/template-foundation/
                        Requirements, design, tests, threat model, and traceability
docs/                   ADRs, architecture views, adoption guides, and runbooks
scripts/                Bootstrap, validation, and repository security tooling
```

## Create a derived project

1. Copy `template.config.example.json` to an ignored `template.config.json`.
2. Replace every example value with the new project's identifiers.
3. Run the bootstrap without credentials or cloud project secrets:

   ```text
   python scripts/bootstrap_template.py --config template.config.json
   ```

4. Review the generated names and `.github/CODEOWNERS` before the first commit.
5. Install dependencies and local hooks:

   ```text
   pnpm install --frozen-lockfile
   uv sync --all-packages --all-extras
   uv run python scripts/install_repository_hooks.py
   ```

6. Run the complete local gate:

   ```text
   powershell -ExecutionPolicy Bypass -File scripts/validate.ps1
   ```

The bootstrap changes identifiers only. Product requirements, cloud regions, IAM,
budgets, domains, and deployment environments remain explicit decisions for each
derived project.

## Local development

Copy `.env.example` to `.env`, replace only the local placeholder passwords, then run:

```text
pnpm emulators:firebase
docker compose up --build
```

The web application is available at `http://localhost:3000`; liveness and readiness are
available at `http://localhost:8000/health/live` and `/health/ready`.

Development-header authentication is rejected in staging and production. The local API
uses a non-owner PostgreSQL identity so ordinary traffic exercises forced RLS.

## Architecture and security

The frontend never authorizes protected behavior. The control plane validates identity,
resolves tenant membership, and supplies trusted tenant context. Firestore client writes
remain denied; server access requires least-privilege IAM. Cross-store workflows must
use the documented outbox/inbox and reconciliation protocol.

See [AGENTS.md](AGENTS.md), [system context](docs/architecture/system-context.md), the
[template specification](specs/template-foundation/requirements.md), and the
[secret-management runbook](docs/runbooks/secret-management.md).

## Delivery model

Use protected `main` and `develop` branches plus short-lived workstream branches. CI must
pass before promotion, production promotion is never automatic, and Google Cloud access
uses short-lived Workload Identity Federation rather than service-account key files.

## License

Licensed under the [Apache License 2.0](LICENSE). Derived projects must preserve the
license and applicable notices unless their legal owner explicitly chooses another
compatible arrangement.
