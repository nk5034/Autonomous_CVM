"""Campaign simulation endpoints (Phase 9)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.security.rbac import require_permissions
from src.schemas.simulation import (
    CampaignSimulationRequest,
    CampaignSimulationResponse,
    CampaignSimulationTemplateResponse,
)
from src.services.campaign_simulation import CampaignSimulationService

router = APIRouter(prefix="/campaign-simulation", tags=["campaign-simulation"])
simulation_service = CampaignSimulationService()


@router.get("/config/template", response_model=CampaignSimulationTemplateResponse)
async def get_simulation_template(
    _: object = Depends(require_permissions(["campaign.simulation.read"])),
) -> CampaignSimulationTemplateResponse:
    return simulation_service.get_template()


@router.post("/run", response_model=CampaignSimulationResponse)
async def run_simulation(
    payload: CampaignSimulationRequest,
    _: object = Depends(require_permissions(["campaign.simulation.run"])),
) -> CampaignSimulationResponse:
    return simulation_service.run(payload)
