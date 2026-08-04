# Template foundation design

## Design

The baseline is a moderately modular monorepo. Next.js owns presentation and server-side
web behavior; Python Cloud Run services own trusted application behavior; narrow Cloud
Functions adapt events; PostgreSQL owns relational authority; Firestore exposes only
sanitized real-time projections. Contracts remain versioned independently from storage.

Adoption is a one-way local transformation. `template.config.json` is ignored, validated
against a closed schema, and applied by a standard-library Python script. The script
renames the default Python package, creates CODEOWNERS from an example, and replaces only
documented identity tokens. It performs no network, Git, or cloud operation.

## Boundaries

The template supplies seams for future orchestrators, jobs, functions, event contracts,
telemetry, and model operations. Phase 2 deliberately supplies no agent runtime, model
registry, prompt registry, evaluation pipeline, training pipeline, or vertical workflow.

## Data and security

Trusted identity establishes tenant context. PostgreSQL row-level security is defense in
depth for tenant-owned relational data. Firestore client writes are denied by default.
Execution identities and credentials must be short-lived and separated from the control
plane. Repository hooks and CI scan for sensitive filenames and high-confidence secrets.
