# Baseline frontend

This directory is the Next.js application root and the Firebase App Hosting target for
the pnpm/Turborepo monorepo.

## Hosting

App Hosting is the baseline because the application uses dynamic server rendering. It
builds the Next.js application into a managed Cloud Run revision and serves it through
Cloud CDN. Traditional Firebase Hosting is retained only as a future option for a fully
static export or an explicit rewrite to a separately operated Cloud Run service.

`apphosting.yaml` contains safe shared runtime defaults.
`apphosting.<environment>.yaml` files may override them after separate Firebase projects,
regions, API URLs, budgets, and rollout policies are approved.

Development may use automatic rollouts. Staging and production use manually triggered,
auditable rollouts for a validated commit.

## Security boundary

Firebase Authentication establishes identity. The control plane verifies the ID token
and authorizes every protected operation. App Check may add an anti-abuse token but never
replaces authentication or authorization.

Direct Firestore access is limited to sanitized read-only projections protected by
Identity Platform tenant claims. All mutations go through a trusted backend.
