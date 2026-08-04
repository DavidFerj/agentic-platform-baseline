# ADR-0003: Separate the secure execution plane

Status: Accepted
Date: 2026-07-29

## Context

Coding agents execute untrusted repository code, shell commands, package installers, and
network calls. Sharing the control-plane process or service identity would increase the
impact of prompt injection, malicious dependencies, and tool abuse.

## Decision

Execute coding tasks in ephemeral runners or jobs with task-scoped identity, disposable
filesystem, bounded compute/time/cost, egress allowlists, and no production credentials.
The control plane authorizes and observes work through explicit task/evidence contracts.

## Consequences

- Local Docker workspaces are acceptable for the MVP if their boundaries are explicit.
- Cloud executor selection remains open until build and isolation requirements are
  measured.
- Artifact capture and audit must complete before workspace teardown.
- Synchronous in-process coding-agent execution is prohibited.
