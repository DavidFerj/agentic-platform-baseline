"""Versioned platform information."""

from typing import Annotated

from fastapi import APIRouter, Depends

from platform_api.api.dependencies import get_settings
from platform_api.contracts.operational import PlatformInfo
from platform_api.core.config import Settings

router = APIRouter(tags=["platform"])


@router.get("/platform", response_model=PlatformInfo)
async def platform_information(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlatformInfo:
    """Describe the implemented foundation without overstating future capability."""
    return PlatformInfo(
        product=settings.product_name,
        short_name=settings.product_short_name,
        version=settings.build_version,
        phase="foundation",
        north_star=(
            "Provide a secure, observable, multi-tenant foundation that vertical "
            "products can extend without inheriting product-specific behavior."
        ),
        implemented_capabilities=[
            "versioned-template-specification",
            "operational-api",
            "tenant-aware-data-schema",
            "accessible-product-shell",
            "local-reproducible-stack",
        ],
        deferred_capabilities=[
            "vertical-domain",
            "agent-orchestration",
            "model-lifecycle",
            "cloud-provisioning",
            "staging-deployment",
        ],
    )
