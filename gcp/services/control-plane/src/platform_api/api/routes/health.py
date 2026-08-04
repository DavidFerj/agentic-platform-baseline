"""Liveness and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from platform_api.api.dependencies import get_database
from platform_api.api.errors import ServiceUnavailableError
from platform_api.contracts.operational import HealthResponse, ProblemDetail
from platform_api.infrastructure.database import DatabaseGateway

router = APIRouter(prefix="/health", tags=["operations"])


@router.get("/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    """Confirm that the API process can serve requests."""
    return HealthResponse(status="live", dependencies={})


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"model": ProblemDetail}},
)
async def readiness(
    database: Annotated[DatabaseGateway, Depends(get_database)],
) -> HealthResponse:
    """Confirm that required control-plane dependencies are available."""
    try:
        await database.ping()
    except SQLAlchemyError as error:
        raise ServiceUnavailableError(
            code="database_unavailable",
            detail="A required data service is unavailable.",
        ) from error

    return HealthResponse(status="ready", dependencies={"database": "ready"})
