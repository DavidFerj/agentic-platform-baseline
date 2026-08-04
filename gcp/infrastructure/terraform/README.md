# Google Cloud infrastructure boundary

Terraform resource creation is intentionally deferred until the product owner approves
the GCP project, regions, environments, domains, budget, identity model, and state
bootstrap.

The first implementation will cover:

- separate development, staging, and production projects or equivalent hard boundaries;
- Firebase App Hosting for the Next.js frontend;
- Cloud Run services for the control plane and orchestrator;
- Cloud Run functions only for narrow HTTP or CloudEvent adapters;
- Cloud Run jobs for migrations and isolated finite execution;
- Firebase Authentication with Identity Platform and App Check;
- Cloud Firestore for operational state and sanitized real-time projections;
- a separately authorized migration job;
- Cloud SQL for PostgreSQL with private connectivity;
- Cloud Storage for DSP/evidence/artifacts;
- Pub/Sub and Cloud Tasks for asynchronous work;
- Secret Manager and least-privilege service accounts;
- Artifact Registry;
- OpenTelemetry export to Cloud Logging/Trace/Monitoring;
- workload identity federation from protected GitHub environments;
- budget alerts, retention, backups, health checks, and rollback configuration.

No remote state bucket, IAM binding, API enablement, or billable resource is created by
the foundation because those actions require environment-specific approval.

Development, staging, and production use separate Firebase/GCP projects. App Hosting
automatic rollouts are permitted only for development; higher environments use explicit,
auditable rollouts after their quality gates.
