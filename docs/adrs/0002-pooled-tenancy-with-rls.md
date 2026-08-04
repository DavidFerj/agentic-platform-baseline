# ADR-0002: Use pooled tenancy with PostgreSQL Row-Level Security

Status: Accepted
Date: 2026-07-29

## Context

The MVP needs tenant-aware behavior without the cost of a database or project per tenant.
Application-only filters are vulnerable to omissions and do not provide sufficient
defense in depth.

## Decision

Use shared PostgreSQL tables with a mandatory `tenant_id` on tenant-owned records. The
API derives tenant context from validated identity, scopes repositories explicitly, and
sets `app.tenant_id` inside the transaction. Forced RLS policies restrict reads and
writes to that trusted context.

## Consequences

- Efficient pooled operation is suitable for the MVP.
- Every request, job, migration, unique key, and test must consider tenant context.
- Database owners and migration identities require careful separation because PostgreSQL
  superusers can bypass RLS.
- Application services use a separate non-owner `NOBYPASSRLS` role. Migrations run as a
  one-shot job before application replicas receive traffic.
- Tenant-owned foreign keys include the tenant dimension when a global identifier alone
  could cross a security boundary.
- Bridge or silo models remain future options for enterprise isolation requirements.
