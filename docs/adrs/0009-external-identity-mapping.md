# ADR-0009: Qualify and map external identities explicitly

## Status

Accepted

## Context

Firebase Authentication and Identity Platform subjects are not globally unique across
issuers or identity tenants. Treating a bare `sub` claim as a platform user or trusting a
tenant identifier supplied by the browser can bind a request to the wrong customer.

## Decision

An external identity is identified by the immutable tuple:

`(issuer, identity_tenant, subject)`

`identity_tenant_mappings` maps `(issuer, identity_tenant)` one-to-one to an internal
tenant UUID. The mapping is provisioned through an audited administrative workflow, not
created implicitly during login.

Authentication proceeds in this order:

1. Verify token signature, issuer, audience, expiry, and authentication time using the
   platform SDK.
2. Normalize the verified issuer and identity-tenant claims.
3. Resolve the external tenant mapping from trusted server-side storage.
4. Resolve the qualified user identity.
5. Load active internal membership and authorization.
6. Establish transaction-scoped tenant context for persistence.

The browser never selects or overrides the effective tenant. Identity mapping records are
not exposed through general APIs and require a dedicated administrative permission.

## Consequences

- The relational schema stores issuer and identity tenant with each subject.
- A Firebase tenant cannot be attached to more than one internal tenant, and an internal
  tenant cannot silently acquire multiple external identity tenants.
- Subject reassignment, tenant transfer, and account linking require explicit audited
  workflows.
- Authentication implementation must include negative tests for unknown issuers,
  unknown mappings, cross-tenant subjects, disabled memberships, and stale tokens.
