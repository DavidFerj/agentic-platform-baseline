"""PostgreSQL integration coverage for the tenant-isolation boundary."""

import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from psycopg import sql

POSTGRES_URL = os.getenv("PLATFORM_TEST_POSTGRES_URL")
API_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    POSTGRES_URL is None,
    reason="PLATFORM_TEST_POSTGRES_URL is required for PostgreSQL integration tests",
)


def _alembic_config() -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "migrations"))
    config.set_main_option("prepend_sys_path", str(API_ROOT / "src"))
    return config


def _psycopg_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


def test_rls_denies_missing_and_mismatched_tenant_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert POSTGRES_URL is not None
    sync_url = _psycopg_url(POSTGRES_URL)
    monkeypatch.setenv("PLATFORM_DATABASE_URL", POSTGRES_URL)
    migration_config = _alembic_config()
    command.upgrade(migration_config, "head")

    role_name = f"platform_rls_test_{uuid4().hex}"
    tenant_a = uuid4()
    tenant_b = uuid4()
    user_id = uuid4()
    workspace_a = uuid4()
    workspace_b = uuid4()
    audit_event_id = uuid4()
    role_created = False

    try:
        with (
            psycopg.connect(sync_url, autocommit=True) as admin,
            admin.cursor() as cursor,
        ):
            cursor.execute(
                """
                SELECT relname, relrowsecurity, relforcerowsecurity
                FROM pg_class
                WHERE relname = ANY(%s)
                ORDER BY relname
                """,
                (["audit_events", "projects", "memberships", "workspaces"],),
            )
            assert cursor.fetchall() == [
                ("audit_events", True, True),
                ("memberships", True, True),
                ("projects", True, True),
                ("workspaces", True, True),
            ]

            cursor.execute(
                """
                INSERT INTO tenants (id, slug, display_name)
                VALUES (%s, %s, %s), (%s, %s, %s)
                """,
                (tenant_a, "tenant-a", "Tenant A", tenant_b, "tenant-b", "Tenant B"),
            )
            cursor.execute(
                """
                INSERT INTO users (id, issuer, identity_tenant, subject, email)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    "https://securetoken.google.com/platform-test",
                    "tenant-test",
                    "test-subject",
                    "test@example.invalid",
                ),
            )
            cursor.execute(
                """
                INSERT INTO workspaces (id, tenant_id, name, created_by)
                VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
                """,
                (
                    workspace_a,
                    tenant_a,
                    "Workspace A",
                    user_id,
                    workspace_b,
                    tenant_b,
                    "Workspace B",
                    user_id,
                ),
            )
            with pytest.raises(psycopg.errors.ForeignKeyViolation):
                cursor.execute(
                    """
                    INSERT INTO projects (
                      id, tenant_id, workspace_id, name, description, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        tenant_a,
                        workspace_b,
                        "Cross-tenant project",
                        "Must be rejected by the composite foreign key.",
                        "DRAFT",
                    ),
                )
            cursor.execute(
                """
                INSERT INTO audit_events (
                  id, tenant_id, actor_id, action, resource_type,
                  resource_id, request_id, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    audit_event_id,
                    tenant_a,
                    user_id,
                    "workspace.created",
                    "workspace",
                    str(workspace_a),
                    "rls-test",
                    "{}",
                ),
            )
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cursor.execute(
                    "UPDATE audit_events SET action = %s WHERE id = %s",
                    ("tampered", audit_event_id),
                )
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cursor.execute("DELETE FROM audit_events WHERE id = %s", (audit_event_id,))

            cursor.execute(
                """
                SELECT policyname, cmd
                FROM pg_policies
                WHERE tablename = 'audit_events'
                ORDER BY policyname
                """
            )
            assert cursor.fetchall() == [
                ("audit_events_tenant_insert", "INSERT"),
                ("audit_events_tenant_read", "SELECT"),
            ]
            cursor.execute(
                sql.SQL(
                    "CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB "
                    "NOCREATEROLE NOINHERIT NOBYPASSRLS"
                ).format(sql.Identifier(role_name))
            )
            role_created = True
            cursor.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(role_name))
            )
            cursor.execute(
                sql.SQL("GRANT SELECT, INSERT ON TABLE workspaces TO {}").format(
                    sql.Identifier(role_name)
                )
            )

        with (
            psycopg.connect(sync_url) as application_connection,
            application_connection.cursor() as cursor,
        ):
            cursor.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role_name)))
            cursor.execute("SELECT count(*) FROM workspaces")
            assert cursor.fetchone() == (0,)
            cursor.execute(
                "SELECT set_config('app.tenant_id', %s, true)",
                (str(tenant_a),),
            )
            cursor.execute("SELECT name FROM workspaces ORDER BY name")
            assert cursor.fetchall() == [("Workspace A",)]

        with (
            psycopg.connect(sync_url) as application_connection,
            application_connection.cursor() as cursor,
        ):
            cursor.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role_name)))
            cursor.execute(
                "SELECT set_config('app.tenant_id', %s, true)",
                (str(tenant_a),),
            )
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cursor.execute(
                    """
                    INSERT INTO workspaces (id, tenant_id, name, created_by)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (uuid4(), tenant_b, "Cross-tenant write", user_id),
                )
            application_connection.rollback()
    finally:
        if role_created:
            with (
                psycopg.connect(sync_url, autocommit=True) as admin,
                admin.cursor() as cursor,
            ):
                cursor.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(role_name)))
                cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role_name)))
        command.downgrade(migration_config, "base")
