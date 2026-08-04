# Local development runbook

## Start

1. Copy `.env.example` to `.env`.
2. Replace every placeholder password. Owner and runtime passwords must differ.
3. Install Java 21 and run `pnpm emulators:firebase` in a dedicated terminal.
4. Run `docker compose config` and inspect the resolved configuration for unexpected
   ports, mounts, or values.
5. Run `docker compose up --build`.
6. Confirm the one-shot `migrate` service completes successfully.
7. Wait for PostgreSQL, API, and web health checks.

## Verify

- Web: `http://localhost:3000`
- API liveness: `http://localhost:8000/health/live`
- API readiness: `http://localhost:8000/health/ready`
- OpenAPI UI: `http://localhost:8000/docs`
- MinIO console: `http://localhost:9001`
- Firebase Emulator UI: `http://127.0.0.1:4000`
- Firestore emulator: `127.0.0.1:8080`
- Authentication emulator: `127.0.0.1:9099`

Do not use local credentials outside this environment.

## Stop

Run `docker compose down`. Named volumes preserve local development state. To request a
destructive reset, identify the exact project volumes and obtain explicit authorization
before removing them.

## Diagnose

- API live but not ready: inspect PostgreSQL health and API logs using the request ID.
- Web reports unavailable: confirm the API URL and that server-side web networking can
  resolve `api`.
- Migration failure: stop API replicas, inspect the Alembic revision, and do not modify
  the database manually.
- Runtime receives unexpected data: confirm the API URL uses `POSTGRES_APP_USER`, verify
  that the role is `NOSUPERUSER NOBYPASSRLS`, and inspect transaction tenant context.
- Resource pressure: stop MinIO/telemetry first or run only `postgres api web`.
- Emulator startup failure: verify Java 21 and run `pnpm exec firebase --version`.
