# Cross-store projection recovery

## Trigger conditions

Use this runbook for a dead-letter event, aggregate-version gap, stale Firestore
projection, expired outbox lease, or a PostgreSQL/Firestore reconciliation alert.

## Safety

- Treat PostgreSQL as authoritative.
- Do not patch PostgreSQL from Firestore.
- Do not create a new idempotency key to force a duplicate side effect.
- Preserve event, correlation, causation, aggregate, and attempt identifiers.
- Never copy payloads containing Restricted data into tickets or chat.

## Diagnosis

1. Identify tenant, aggregate, expected version, projection version, consumer, and
   idempotency key from safe metadata.
2. Confirm the authoritative PostgreSQL transaction and outbox record.
3. Inspect inbox status and lease expiry.
4. Classify the failure as transient dependency, contract rejection, version gap,
   authorization/IAM, poison payload, or implementation defect.
5. Stop redrive if the contract or authorization is invalid.

## Recovery

- For an expired lease, release it only after confirming no active worker owns it.
- For a transient dependency failure, redrive the original event.
- For a version gap, replay missing versions in order or rebuild the projection from an
  approved authoritative snapshot.
- For a poison event, fix the producer or compatible consumer first; do not mutate the
  original event.
- For a compromised or cross-tenant event, disable redrive, preserve evidence, and invoke
  the security incident process.

## Verification

Confirm that the projection version matches PostgreSQL, the inbox records one completed
effect, no duplicate external side effect occurred, backlog and age return below alert
thresholds, and an append-only audit event records the operator action.
