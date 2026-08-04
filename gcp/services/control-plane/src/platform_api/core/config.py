"""Environment-backed application configuration."""

from enum import StrEnum

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class AuthMode(StrEnum):
    """Identity adapters supported by configuration."""

    DEVELOPMENT = "development"
    OIDC = "oidc"


class Settings(BaseSettings):
    """Validated settings loaded from the process environment."""

    model_config = SettingsConfigDict(
        env_prefix="PLATFORM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    product_name: str = "Agentic Platform Baseline"
    product_short_name: str = "APB"
    build_version: str = "0.1.0"
    environment: Environment = Environment.DEVELOPMENT
    auth_mode: AuthMode = AuthMode.DEVELOPMENT
    database_url: str = Field(repr=False)
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=5, ge=0, le=20)
    database_pool_timeout_seconds: int = Field(default=5, ge=1, le=30)
    database_statement_timeout_ms: int = Field(default=15_000, ge=1_000, le=120_000)
    cors_origins: str = ""
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    docs_enabled: bool | None = None

    @model_validator(mode="after")
    def reject_development_auth_outside_safe_environments(self) -> "Settings":
        """Fail closed if development identity reaches a shared environment."""
        safe_environments = {Environment.DEVELOPMENT, Environment.TEST}
        if self.environment not in safe_environments and self.auth_mode is AuthMode.DEVELOPMENT:
            raise ValueError("development authentication is forbidden outside development/test")
        return self

    @property
    def cors_origin_list(self) -> tuple[str, ...]:
        """Normalize comma-separated origins and remove empty entries."""
        return tuple(origin.strip() for origin in self.cors_origins.split(",") if origin.strip())

    @property
    def api_docs_enabled(self) -> bool:
        """Expose API discovery only by explicit opt-in outside local/test environments."""
        if self.docs_enabled is not None:
            return self.docs_enabled
        return self.environment in {Environment.DEVELOPMENT, Environment.TEST}
