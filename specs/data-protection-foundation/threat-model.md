# Data protection foundation threat model

| Asset                | Threat or abuse case                                  | Phase 3A mitigation                                                  | Residual risk / owner                                                         |
| -------------------- | ----------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Tenant boundary      | Client forges tenant, actor, or role                  | Domain requires trusted context; no public API added                 | Authentication adapter must enforce this before runtime use / Identity        |
| Processing authority | Missing or false purpose/authority permits use        | Explicit allowlists; missing consent reference denies                | Authority records and legal validity need workflow and review / Privacy-Legal |
| Sensitive data       | Restricted data sent to an unapproved provider/region | Provider, region, and classification mismatches deny                 | Egress and provider gateway must enforce obligations / Platform-Security      |
| Policy integrity     | Policy silently changes behavior                      | Policy ID/version plus deterministic fingerprint and reviewable code | Policy signing and controlled rollout are deferred / Platform                 |
| Evidence             | Logs or records capture source content/secrets        | Evidence contract includes metadata only and forbids extra fields    | Callers could log unsafe context outside this module / SRE-Security           |
| Human control        | Consequential action bypasses approval                | Configured actions return mandatory approval obligation              | Runtime workflow must make obligation non-bypassable / Product-Security       |
| Legal claims         | A framework entry is represented as certification     | Explicit disclaimer and overlays disabled pending approval           | Applicability evolves; continuous legal review required / Legal               |
| AI manipulation      | Prompt or model output changes a control decision     | Deterministic engine has no model/provider dependency                | Future gateways must keep model output non-authoritative / AI Governance      |

Security-blocking integration rule: no external caller may use the engine as an
authorization oracle until authentication, tenant membership, input validation, policy
selection, audit persistence, and obligation enforcement are implemented together.
