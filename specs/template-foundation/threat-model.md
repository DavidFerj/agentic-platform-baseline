# Template foundation threat model

## Assets and boundaries

Assets include source integrity, tenant data, deployment identities, audit evidence,
contracts, and adopter configuration. Boundaries exist at browser/backend, service/service,
CI/cloud, Firebase/server SDK, tenant/tenant, and template/adopter inputs.

## Principal threats and mitigations

| Threat                                          | Mitigation                                                                   | Residual risk                                                        |
| ----------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Secret committed during adoption                | ignored local config, hooks, CI scanning, credential filename denylist       | Novel secret formats require review and provider scanning            |
| Malicious identity value changes code structure | closed schema and strict identifier patterns                                 | Display name remains free text but is used only as text replacement  |
| Cross-tenant access                             | trusted tenant context, RLS, deny-by-default rules, membership authorization | Future endpoints must preserve these controls                        |
| CI supply-chain compromise                      | immutable action SHAs, least permissions, keyless federation                 | Approved dependencies still require update review                    |
| Template mistaken for complete AgentOps/MLOps   | explicit deferred-capability contracts and documentation                     | Adopters can still overstate their derived implementation            |
| Bootstrap run in the wrong directory            | required root markers and local-only behavior                                | Transformation is not automatically reversible; use a clean checkout |

No production credentials, endpoints, customer data, or provider project identifiers are
part of the baseline.
