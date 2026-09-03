"""API V1 Router"""
from fastapi import APIRouter

from src.api.v1.endpoints.ab_testing import router as ab_testing_router
from src.api.v1.endpoints.campaign_artifacts import router as campaign_artifacts_router
from src.api.v1.endpoints.campaign_simulation import router as campaign_simulation_router
from src.api.v1.endpoints.metadata import router as metadata_router
from src.api.v1.endpoints.synthetic_data import router as synthetic_data_router
from src.api.v1.endpoints.workflow import router as workflow_router

api_router = APIRouter()
api_router.include_router(metadata_router)
api_router.include_router(campaign_artifacts_router)
api_router.include_router(synthetic_data_router)
api_router.include_router(campaign_simulation_router)
api_router.include_router(ab_testing_router)
api_router.include_router(workflow_router)

@api_router.get("/")
async def root():
    return {"message": "CVM Catalyst API v1"}
