# Cloud Run jobs

Jobs execute bounded work and exit. Planned uses include database migrations, repository
analysis, artifact processing, and isolated delivery execution.

Every job must define:

- an idempotent task contract and correlation identifier;
- maximum duration, retries, concurrency, CPU, memory, and cost guardrails;
- task-scoped service identity and secret access;
- input/output persistence and partial-failure recovery;
- safe cancellation and evidence preservation;
- no implicit production promotion.

Long-running agent execution belongs here rather than in an HTTP function. Customer-code
execution remains separated from the control plane by identity, filesystem, credentials,
network policy, and lifecycle.
