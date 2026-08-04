# Database migration runbook

## Local upgrade

From `gcp/services/control-plane` with `PLATFORM_DATABASE_URL` configured:

```text
uv run alembic upgrade head
```

## Pre-deployment checks

- review generated SQL;
- confirm tenant keys, indexes, foreign keys, RLS enable/force, and policies;
- test upgrade and downgrade against disposable data;
- identify locks, duration, compatibility window, and rollback;
- back up staging before destructive or high-risk changes.

## Cloud rollout

Run migrations as a separately authorized job before increasing application traffic.
Application startup must not race migrations across replicas. Destructive migrations use
expand/migrate/contract stages and require explicit authorization.

The migration identity owns schema changes and must never serve application traffic. The
runtime identity is a non-owner with `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, and
`NOBYPASSRLS`. Validate grants and RLS behavior after every migration.

The initial migration is additive. Its rollback deletes all foundation tables and is
therefore destructive; use only against disposable environments.
