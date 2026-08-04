# ADR-0004: Use develop as integration and main as release

Status: Accepted
Date: 2026-07-29

## Context

The product brief requires a protected, deployable `main` branch. The repository also
requires a `develop` integration branch for the staged delivery workflow.

## Decision

- `main` is protected and represents release-ready state.
- `develop` is the normal integration target.
- Short-lived branches are created from the appropriate local baseline and contain one
  independent outcome.
- Staging releases are tagged after authorized integration.
- Production uses a separate workflow with explicit approval.

## Consequences

This adds one integration step compared with pure trunk-based development but preserves
the requested branch model. Branches should remain short-lived to limit divergence.
