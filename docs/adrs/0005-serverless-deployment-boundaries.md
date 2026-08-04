# ADR-0005: Use behavior-aligned serverless deployment boundaries

Status: Accepted
Date: 2026-07-29

## Context

The backend must run serverlessly on Google Cloud. Treating every internal service,
class, or operation as a Cloud Run function would create excessive deployments, network
calls, identities, cold starts, and distributed consistency problems.

## Decision

Organize backend code under `gcp/` by runtime:

- Cloud Run services for cohesive HTTP APIs and orchestration;
- Cloud Run functions for narrow HTTP or CloudEvent adapters;
- Cloud Run jobs for finite execution and migrations.

The control plane remains a modular monolith inside one Cloud Run service until scaling,
security, ownership, or lifecycle evidence justifies extraction.

## Consequences

- Internal modularity does not create accidental network boundaries.
- Each real deployable owns its dependencies, tests, IAM identity, configuration, and
  rollout.
- Event functions must be idempotent and define retry/dead-letter behavior.
- The repository remains GCP-first while domain code stays independent of provider SDKs.
