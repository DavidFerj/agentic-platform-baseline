"""Operational API DTOs."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Forbid undocumented output fields at public boundaries."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(StrictModel):
    """Liveness or readiness state."""

    status: Literal["live", "ready"]
    dependencies: dict[str, Literal["ready"]]


class ProblemDetail(StrictModel):
    """RFC 9457-inspired safe public error response."""

    type: str
    title: str
    status: int = Field(ge=400, le=599)
    detail: str
    code: str
    request_id: str


class PlatformInfo(StrictModel):
    """Foundation capabilities exposed by the platform."""

    product: str
    short_name: str
    version: str
    phase: Literal["foundation"]
    north_star: str
    implemented_capabilities: list[str]
    deferred_capabilities: list[str]
