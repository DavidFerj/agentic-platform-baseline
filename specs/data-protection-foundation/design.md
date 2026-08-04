# Data protection foundation design

## Boundary

`platform_api.domain.data_protection` is a pure control-plane domain module. It accepts a
`PolicyContext` assembled only after authentication, tenant resolution, normalization,
and boundary validation. It evaluates one immutable `ProtectionPolicy` and returns a
`PolicyDecision`. Transport, storage, policy selection, and obligation execution remain
outside the domain.

```text
trusted identity + tenant + declared processing facts
                       |
                       v
             versioned protection policy
                       |
                       v
       deterministic fail-closed decision engine
                       |
           +-----------+------------+
           |            |            |
         permit        deny    require_approval
           +------------+------------+
                        |
        reasons + obligations + evidence fingerprint
```

All policy mismatch reasons are aggregated to improve safe diagnostics and tests. A
denied decision carries only the audit obligation. A non-denied decision adds retention
and classification-specific minimization/redaction duties; configured consequential
actions add human approval.

The fingerprint canonicalizes sets by sorting, serializes all decision inputs and
outputs, and hashes the result with SHA-256. It proves reproducibility and detects drift;
it is not a digital signature and does not establish non-repudiation. Persistence must
also record evaluation time and immutable audit metadata in a later integration.

No policy decision is delegated to a language model. Framework profiles guide control
design, while legal and assurance overlays are inactive until accountable review.
