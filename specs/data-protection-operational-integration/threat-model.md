# Threat model

| Threat                        | Mitigation                                      | Residual control                  |
| ----------------------------- | ----------------------------------------------- | --------------------------------- |
| Forged tenant, actor, or role | Only `TenantContext` supplies identity facts.   | Add Firebase/OIDC verification.   |
| Weaker policy selection       | Exact server-controlled policy version.         | Add policy approval provenance.   |
| Unaudited decision            | Append completes before return; failure blocks. | Add operational alerting.         |
| Duplicate retry               | Unique request key and fingerprint comparison.  | Concurrent conflicts fail closed. |
| Sensitive evidence            | Explicit metadata-only serializer.              | Add DLP monitoring.               |
