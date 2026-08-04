# ADR-0006: Adopt Firebase as a constrained BaaS layer

Status: Accepted
Date: 2026-07-29

## Context

The baseline needs managed authentication, real-time workflow state, and local emulation while
retaining relational tenancy, policy, audit, and release guarantees.

## Decision

Use Firebase Authentication for identity and plan the Identity Platform upgrade for B2B
tenant claims, MFA, and enterprise federation. Use Firestore for orchestration state,
checkpoints, progress, and sanitized real-time projections. Retain PostgreSQL for
relational tenancy, memberships, approvals, audit, billing, and releases.

Client Firestore writes are denied. Tenant-scoped projection reads require the
Identity Platform tenant claim. Trusted services write through server SDKs using
least-privilege IAM. App Check is supplemental abuse protection, not authorization.

## Consequences

- The frontend can receive real-time state without owning business authorization.
- Server SDK access must be governed by IAM because it bypasses Security Rules.
- Cross-store workflows are not atomic and require idempotency, correlation, and repair.
- Identity Platform tenant IDs must map explicitly to internal tenant UUIDs.
- Separate Firebase/GCP projects are required for development, staging, and production.
