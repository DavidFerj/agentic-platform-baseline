# Firebase BaaS boundary

Firebase is part of the GCP platform boundary, not a second authorization system.

## Selected services

| Service                   | Baseline responsibility                                               |
| ------------------------- | --------------------------------------------------------------------- |
| Firebase App Hosting      | Dynamic Next.js hosting on managed Cloud Run/CDN                      |
| Firebase Authentication   | End-user identity and provider federation                             |
| Identity Platform upgrade | B2B tenant claims, MFA, SAML/OIDC, audit/SLA                          |
| Cloud Firestore           | Orchestration state, checkpoints, progress, and sanitized projections |
| Local Emulator Suite      | Auth, Firestore, and App Hosting development/testing                  |
| Firebase App Check        | Supplemental anti-abuse protection before public beta                 |

Remote Config, Analytics, Cloud Messaging, Realtime Database, and Extensions are not
baseline dependencies. They require a concrete requirement before adoption.

## Firestore namespaces

```text
tenants/{identityPlatformTenantId}/
  runProjections/{runId}                       sanitized, read-only projection
  projectProjections/{projectId}         sanitized, read-only projection

internal/                    server-only operational state and checkpoints
```

The repository rules allow tenant-scoped reads only from the two projection collections
when the validated token's `firebase.tenant` matches the path. Every client write and
every other path is denied.

Server SDKs bypass Firestore Security Rules. Each Cloud Run service/function/job
therefore uses its own user-managed service account and the narrowest Firestore IAM role.
Service-account key files and `GOOGLE_APPLICATION_CREDENTIALS` are forbidden in deployed
Cloud Run resources.

The application tenant remains an internal PostgreSQL UUID. Before enabling direct
projection reads, provisioning must persist and audit the one-to-one mapping between that
UUID and the Identity Platform tenant ID.

## Local use

Install Java 21, then run from the repository root:

```text
pnpm emulators:firebase
pnpm test:firebase
```

The committed project ID `agentic-platform-local` is emulator-only. Real environments use separate
Firebase/GCP projects and local `.firebaserc` aliases that are intentionally ignored.
