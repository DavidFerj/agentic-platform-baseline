# ADR-0007: Use Firebase App Hosting for the Next.js application

Status: Accepted
Date: 2026-07-29

## Context

The frontend is a dynamic Next.js application. Traditional Firebase Hosting is optimized
for static assets and needs an additional Cloud Run rewrite for server-rendered content.
App Hosting provides native Next.js builds, managed Cloud Run revisions, CDN delivery,
environment configuration, monorepo roots, and rollback.

## Decision

Use Firebase App Hosting with `frontend` as the application root. Declare a minimal
Turborepo task graph over the pnpm workspace so the build follows an officially supported
monorepo path. Keep safe shared runtime defaults in `frontend/apphosting.yaml`. Use a
separate Firebase/GCP project per environment.

Automatic rollouts are allowed only in development. Staging and production rollouts are
triggered explicitly for a validated commit after the applicable approval gate.

## Consequences

- Next.js SSR does not require a custom hosting-to-Cloud-Run bridge.
- App Hosting owns the frontend build container, revision, load balancing, and CDN.
- Blaze billing, region, backend IDs, domains, budgets, and environment-specific API URLs
  require approval before resource creation.
- Traditional Firebase Hosting remains available if the application becomes fully static.

## References

- https://firebase.google.com/docs/app-hosting
- https://firebase.google.com/docs/app-hosting/monorepos
- https://firebase.google.com/docs/app-hosting/rollouts
