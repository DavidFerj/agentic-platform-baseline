# Baseline contracts

Contracts in this package are public boundaries, not persistence models.

- `openapi/control-plane.v1.yaml` defines the synchronous HTTP baseline.
- `events/envelope.v1.schema.json` defines the common metadata for future asynchronous
  events.

Every event type must provide a separate versioned payload schema that composes with the
envelope. Producers use a stable idempotency key for the business effect and a strictly
increasing aggregate version. Consumers reject unknown schema versions, persist the
idempotency key before applying side effects, and treat an already completed key as a
successful duplicate.

Any change must identify producers and consumers, assess backward compatibility, update
tests, and describe rollout requirements. Breaking changes require a new major contract
version.
