"""Phase 10 A/B testing endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.security.rbac import require_permissions
from src.schemas.ab_testing import ABTestingRequest, ABTestingResponse, ABTestingTemplateResponse
from src.services.ab_testing import ABTestingService

router = APIRouter(prefix="/ab-testing", tags=["ab-testing"])
ab_testing_service = ABTestingService()


@router.get("/template", response_model=ABTestingTemplateResponse)
async def get_ab_testing_template(
    _: object = Depends(require_permissions(["ab_testing.read"])),
) -> ABTestingTemplateResponse:
    return ab_testing_service.get_template()


@router.post("/run", response_model=ABTestingResponse)
async def run_ab_testing(
    payload: ABTestingRequest,
    _: object = Depends(require_permissions(["ab_testing.run"])),
) -> ABTestingResponse:
    return ab_testing_service.run(payload)