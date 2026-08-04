# Data protection foundation acceptance criteria

- **AC-DPF-001:** versioned inventory, applicability matrix, and unique control catalog
  are machine-readable and contain no data samples or secrets.
- **AC-DPF-002:** a fully matching context returns `permit` and classification-specific
  obligations.
- **AC-DPF-003:** every supported mismatch is aggregated into stable denial reasons and
  the result fails closed.
- **AC-DPF-004:** consent processing without an evidence reference is denied.
- **AC-DPF-005:** configured export/deletion actions require human approval.
- **AC-DPF-006:** equivalent normalized inputs produce the same fingerprint and a
  material context change produces a different fingerprint.
- **AC-DPF-007:** engine evidence validates against the closed versioned JSON Schema.
- **AC-DPF-008:** framework references are distinguished from legal obligations and all
  legal/assurance overlays remain enforcement-disabled pending approval.
- **AC-DPF-009:** domain tests achieve 100% statement and branch coverage and lint, type,
  architecture, repository-hygiene, and secret gates pass.
- **AC-DPF-010:** design, threat model, test plan, traceability, and actual validation
  evidence describe the implemented boundary and deferred work.
