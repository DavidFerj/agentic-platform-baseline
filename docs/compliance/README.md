# Data protection, privacy, and compliance foundation

This directory defines reusable governance inputs for the Agentic Platform Baseline.
The implementation is a technical control foundation, not a legal opinion,
certification, or representation of compliance with any law or standard.

The control plane evaluates trusted identity and tenant context, declared purpose,
classification, processing authority, provider, and region against a versioned policy.
It returns a deterministic `permit`, `deny`, or `require_approval` result plus explicit
obligations. Denial is the safe default whenever required context does not match policy.

## Governed artifacts

- `control-catalog.yaml`: reusable control objectives and evidence expectations;
- `applicability-matrix.yaml`: inactive framework and legal overlay templates;
- `data-inventory.yaml`: safe examples and required extension points for derived projects;
- `gcp/packages/contracts/compliance/policy-decision.v1.schema.json`: portable evidence
  contract;
- `platform_api.domain.data_protection`: provider-independent decision engine.

Every derived project must replace ownership, scope, processing activities, retention,
providers, regions, and applicability decisions. Legal overlays remain disabled until
counsel and the accountable business owner approve jurisdiction, contractual duties,
and operational evidence. An alignment target is not a certification. Generated or
model-produced text cannot authorize processing.

## Phase boundary

Phase 3A implements deterministic evaluation and governance artifacts. Runtime API
exposure, durable evidence storage, consent and data-subject request workflows,
retention/deletion execution, vendor assessments, breach notification, and continuous
control monitoring are later verticals. Callers remain responsible for enforcing every
returned obligation and recording the decision in the append-only audit boundary.

Phase 3B begins that integration with trusted application context, exact server-side
policy selection, and idempotent append-only decision evidence. Public policy routes
remain disabled until Firebase/OIDC identity and tenant membership are verified.
