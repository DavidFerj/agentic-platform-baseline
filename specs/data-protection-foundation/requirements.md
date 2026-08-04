# Data protection foundation requirements

Status: Approved for implementation
Scope: Phase 3A - deterministic control foundation

## Functional requirements

### DPF-REQ-001 - Governed processing inventory

The repository shall version processing activities, classifications, purposes, systems,
retention classes, and disclosed external providers without storing personal data.

### DPF-REQ-002 - Applicability governance

Framework and regulatory overlays shall record status and approval authority. No legal
or certification overlay shall be enforced or claimed solely by adding it to the matrix.

### DPF-REQ-003 - Deterministic policy evaluation

The domain shall evaluate trusted tenant, actor, role, action, purpose, classification,
authority, provider, region, and consent-evidence context against an explicit versioned
policy without network, database, provider SDK, or model calls.

### DPF-REQ-004 - Fail-closed outcomes

Any policy mismatch shall produce `deny` with stable reason codes. Configured
consequential actions shall produce `require_approval`; all other complete matches may
produce `permit`.

### DPF-REQ-005 - Enforceable obligations

Every decision shall require audit evidence. Non-denied decisions shall require
retention enforcement and classification-appropriate minimization, redaction, and human
approval obligations.

### DPF-REQ-006 - Reproducible evidence

Every decision shall identify the policy and semantic version and include a stable
SHA-256 fingerprint of normalized inputs, policy, outcome, reasons, and obligations.

### DPF-REQ-007 - Versioned contract

Policy evidence shall conform to a closed JSON Schema contract with no undocumented
fields and no source payload, credential, token, prompt, or direct data value.

### DPF-REQ-008 - Traceable control catalog

Reusable control objectives shall map to implementation or evidence artifacts and to
automated verification where applicable.

## Non-functional requirements

- **DPF-NFR-SEC-001:** callers must derive tenant and actor context from authenticated,
  server-trusted identity; an API is out of scope until that integration exists.
- **DPF-NFR-PRV-001:** decision evidence contains identifiers and metadata only, never
  source content or unrestricted payloads.
- **DPF-NFR-REL-001:** evaluation is side-effect-free, deterministic, and safe to retry.
- **DPF-NFR-MNT-001:** the domain remains independent of FastAPI, persistence, Firebase,
  Google Cloud, model providers, and legal-rule vendors.

## Out of scope

Legal advice or compliance certification; public runtime APIs; durable decision storage;
policy administration UI; consent and rights-request workflow; retention/deletion jobs;
vendor assessments; incident notification; AgentOps/MLOps enforcement; production
deployment; and activation of any regulatory overlay.
