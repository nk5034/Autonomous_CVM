"""Phase 8 synthetic data generation endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.security.rbac import require_permissions
from src.schemas.synthetic import (
    SyntheticDataConfigTemplateResponse,
    SyntheticDataGenerationRequest,
    SyntheticDataGenerationResponse,
)
from src.services.synthetic_data import SyntheticDataService

router = APIRouter(prefix="/synthetic-data", tags=["synthetic-data"])
synthetic_data_service = SyntheticDataService()


@router.get("/config/template", response_model=SyntheticDataConfigTemplateResponse)
async def get_synthetic_generation_template(
    _: object = Depends(require_permissions(["synthetic_data.read"])),
) -> SyntheticDataConfigTemplateResponse:
    template = synthetic_data_service.get_generation_template()
    return SyntheticDataConfigTemplateResponse.model_validate(template)


@router.post("/generate", response_model=SyntheticDataGenerationResponse)
async def generate_synthetic_data(
    payload: SyntheticDataGenerationRequest,
    _: object = Depends(require_permissions(["synthetic_data.generate"])),
) -> SyntheticDataGenerationResponse:
    generated = synthetic_data_service.generate_dataset(
        volume=payload.volume,
        random_seed=payload.random_seed,
        include_records=payload.include_records,
        max_inline_records_per_dataset=payload.max_inline_records_per_dataset,
        data_dictionary_path=payload.data_dictionary_path,
        database_model_path=payload.database_model_path,
    )
    return SyntheticDataGenerationResponse.model_validate(generated)
