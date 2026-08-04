# Data protection foundation traceability

| Requirement | Implementation                                    | Verification                   |
| ----------- | ------------------------------------------------- | ------------------------------ |
| DPF-REQ-001 | `docs/compliance/data-inventory.yaml`             | governance registry test       |
| DPF-REQ-002 | `docs/compliance/applicability-matrix.yaml`       | overlay fail-closed test       |
| DPF-REQ-003 | `domain/data_protection/entities.py`, `engine.py` | engine tests, mypy             |
| DPF-REQ-004 | decision engine reason/effect logic               | mismatch and approval tests    |
| DPF-REQ-005 | classification obligation logic                   | parameterized obligation tests |
| DPF-REQ-006 | canonical SHA-256 fingerprint                     | reproducibility test           |
| DPF-REQ-007 | `policy-decision.v1.schema.json`                  | Draft 2020-12 validation test  |
| DPF-REQ-008 | `docs/compliance/control-catalog.yaml`            | unique control-ID test         |

| Acceptance criterion   | Verification                                                        |
| ---------------------- | ------------------------------------------------------------------- |
| AC-DPF-001, AC-DPF-008 | `test_governance_registries_are_versioned_and_overlays_fail_closed` |
| AC-DPF-002             | `test_permit_returns_classification_obligations`                    |
| AC-DPF-003             | `test_all_policy_mismatches_are_reported_and_fail_closed`           |
| AC-DPF-004             | `test_consent_requires_a_nonempty_evidence_reference`               |
| AC-DPF-005             | `test_high_impact_action_requires_human_approval`                   |
| AC-DPF-006             | `test_fingerprint_is_reproducible_and_input_sensitive`              |
| AC-DPF-007             | `test_decision_contract_accepts_engine_evidence`                    |
| AC-DPF-009, AC-DPF-010 | `validation.md` and repository quality gates                        |
