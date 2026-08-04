# ADR-0008: Use transactional outbox and idempotent projections

## Status

Accepted

## Context

PostgreSQL owns relational business state while Firestore owns orchestration state and
sanitized UI projections. They do not share a transaction. A request that writes both
stores directly can leave durable state inconsistent after a timeout, retry, process
crash, or duplicate event delivery.

## Decision

Cross-store changes use an at-least-once event pipeline:

1. The control plane commits the authoritative PostgreSQL change and an outbox record in
   the same transaction.
2. A publisher claims pending outbox records with bounded leases and publishes the
   versioned event envelope.
3. Each consumer atomically claims `(consumer, idempotency_key)` in its inbox before
   applying a side effect.
4. Firestore projection updates run in a Firestore transaction. They apply only when the
   incoming `aggregate_version` is exactly the stored version plus one.
5. A duplicate completed key is acknowledged as success. An older aggregate version is
   ignored as a replay. A version gap is quarantined for reconciliation.
6. The event is acknowledged only after the inbox outcome and projection write are
   durable.

An idempotency key identifies the business effect, not a delivery attempt. Producers do
not reuse a key with a different payload. Every event type has a versioned payload
schema; the generic envelope alone is not publishable.

## Retry and recovery policy

- Retry only transient failures, with full jitter and delays of approximately 5, 30,
  120, 600, and 1,800 seconds.
- Stop automatic delivery after eight total attempts or 24 hours, whichever happens
  first, and route the event to a dead-letter topic.
- Retain inbox deduplication records for at least 35 days. Aggregate versions remain on
  projections for their full lifetime.
- Retain completed outbox records for 90 days, then compact them after audit evidence is
  durable.
- Redrive is an explicit operator action. It preserves `event_id`, `idempotency_key`,
  causation, and correlation metadata.
- A scheduled reconciler compares authoritative aggregate versions with projection
  versions and emits repair requests; it never edits PostgreSQL from Firestore state.

The initial operational target is p95 projection freshness below 30 seconds and
resolution of dead-lettered production events within one business day. These are
service objectives, not a guarantee to external users.

## Consequences

- No workflow may perform an untracked PostgreSQL/Firestore dual write.
- Consumers need durable inbox state and contract tests for duplicate, out-of-order,
  timeout, and poison-message behavior.
- Additional storage and operational tooling are accepted in exchange for deterministic
  recovery and observable consistency.
- Outbox, inbox, publisher, reconciler, and dead-letter infrastructure are implemented
  only with the first cross-store workflow.
