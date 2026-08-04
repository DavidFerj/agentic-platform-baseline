import pytest
from conftest import make_settings
from pydantic import ValidationError

from platform_api.core.config import AuthMode, Environment, Settings


def test_settings_normalize_cors_origins() -> None:
    settings = make_settings(
        cors_origins=" https://one.example, ,https://two.example ",
        log_level="DEBUG",
    )

    assert settings.cors_origin_list == (
        "https://one.example",
        "https://two.example",
    )
    assert settings.log_level == "DEBUG"


def test_shared_environment_rejects_development_authentication() -> None:
    with pytest.raises(ValidationError, match="development authentication is forbidden"):
        make_settings(
            environment=Environment.PRODUCTION,
            auth_mode=AuthMode.DEVELOPMENT,
        )


@pytest.mark.parametrize("environment", [Environment.STAGING, Environment.PRODUCTION])
def test_shared_environment_accepts_oidc(environment: Environment) -> None:
    settings = make_settings(environment=environment, auth_mode=AuthMode.OIDC)

    assert settings.environment is environment
    assert settings.auth_mode is AuthMode.OIDC


def test_log_level_is_restricted() -> None:
    with pytest.raises(ValidationError):
        Settings(
            environment=Environment.TEST,
            database_url="sqlite+aiosqlite:///:memory:",
            log_level="VERBOSE",
        )


def test_api_docs_default_to_closed_in_shared_environments() -> None:
    production = make_settings(
        environment=Environment.PRODUCTION,
        auth_mode=AuthMode.OIDC,
        docs_enabled=None,
    )
    development = make_settings(
        environment=Environment.DEVELOPMENT,
        docs_enabled=None,
    )

    assert production.api_docs_enabled is False
    assert development.api_docs_enabled is True
