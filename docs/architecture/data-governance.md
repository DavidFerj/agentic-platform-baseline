# Data governance baseline

## Classification

| Class                   | Examples                                                   | Baseline handling                                                        |
| ----------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| Public                  | Published documentation, public release metadata           | Integrity controls; no confidentiality requirement                       |
| Internal                | Non-sensitive telemetry, operational configuration         | Authenticated access; bounded retention                                  |
| Confidential            | Specifications, source code, evidence, tenant metadata     | Tenant authorization, encryption, redacted diagnostics                   |
| Restricted              | Credentials, tokens, private keys, regulated/customer data | Secret manager or approved system only; never in Git                     |
| Regulated / high impact | Legally scoped or consequential-decision data              | Approved overlay, human governance, isolated access, continuous evidence |

The highest classification present controls the whole payload. Production data is never
copied into tests, issues, pull requests, screenshots, prompts, or examples.

## Store authority

- PostgreSQL is authoritative for identity mapping, tenancy, membership, authorization,
  approvals, billing, releases, and audit evidence.
- Firestore is authoritative only for current orchestration state, checkpoints, and
  explicitly versioned UI projections.
- Object storage owns immutable or large evidence artifacts referenced by metadata.
- Logs and traces are diagnostic records, not a business system of record.

## Firestore projection allowlist

Every client-readable projection requires a versioned schema and may contain only fields
needed by the corresponding UI. Projections must exclude:

- credentials, tokens, session identifiers, and secret references;
- email addresses or direct personal identifiers unless the approved UI requires them;
- source code, raw prompts, provider payloads, and unrestricted user content;
- authorization policy, billing details, audit payloads, and internal error text.

Server writers derive projections from authoritative records. Clients cannot write or
select the tenant path independently of verified identity.

## Retention and deletion defaults

| Data                                      | Default retention                                 |
| ----------------------------------------- | ------------------------------------------------- |
| Active identity, tenant, membership       | Tenant lifetime plus 30-day recovery window       |
| Terminal orchestration state/checkpoints  | 30 days                                           |
| Superseded UI projections                 | 7 days                                            |
| Specifications, evidence, release records | 365 days unless tenant policy requires longer     |
| Security and audit events                 | At least 365 days; configurable up to seven years |
| Production application logs and traces    | 90 days                                           |
| Development and staging logs              | 30 days                                           |

Legal hold, contractual obligations, and applicable regulation override deletion
schedules. A tenant deletion first revokes access and execution identities, then records
an auditable tombstone, deletes active stores asynchronously, and allows encrypted
backups to expire under their documented schedule. The target completion window is 30
days unless a legal hold applies.

## Encryption, access, and residency

Managed encryption at rest and TLS in transit are mandatory. Production services use
service identities and least-privilege IAM; service-account key files are prohibited.
Region and backup residency are environment configuration and must be approved before
tenant onboarding. Cross-region replication or export requires the same approval.

## Logging and diagnostics

Logs use identifiers, state transitions, latency, and safe error categories. They never
contain credentials, full tokens, database URLs, raw provider responses, source code,
prompt contents, or unrestricted request bodies. Unexpected exceptions record sanitized
stack locations without exception messages or locals.

## Ownership and review

The product owner approves business retention. Security approves Restricted-data flows.
Platform engineering owns backup and deletion evidence. Every new data flow must identify
classification, authority, retention, deletion, consumers, and tenant boundary in its
specification.

## Policy decision foundation

The Phase 3A data-protection engine evaluates trusted identity and tenant context,
purpose, authority, classification, provider, and region before a protected processing
operation. A `permit` is conditional on the caller enforcing every returned obligation;
it is neither legal advice nor proof of compliance. See `docs/compliance/` for the
versioned inventory, control catalog, applicability status, and phase boundary.
