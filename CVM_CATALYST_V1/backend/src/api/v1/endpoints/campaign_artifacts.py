"""Campaign artifact generation and lifecycle endpoints (Phase 6)."""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.settings import settings
from src.core.security.rbac import require_permissions
from src.db.database import get_db
from src.models.entities import CampaignArtifactType as DbCampaignArtifactType
from src.schemas.domain import (
    ArtifactBulkGenerationRequest,
    ArtifactExportResponse,
    ArtifactGenerationRequest,
    ArtifactRollbackRequest,
    ArtifactReviewDecision,
    CampaignArtifactRead,
    CampaignArtifactType,
)
from src.services.artifact_generation import ArtifactType, CampaignArtifactService
from src.services.artifact_generation_db import CampaignArtifactDbService

router = APIRouter(prefix="/campaign-artifacts", tags=["campaign-artifacts"])
artifact_service = CampaignArtifactService()


def _to_service_type(schema_type: CampaignArtifactType) -> ArtifactType:
    return ArtifactType(schema_type.value)


def _to_db_service_type(schema_type: CampaignArtifactType) -> DbCampaignArtifactType:
    return DbCampaignArtifactType(schema_type.value)


def _use_db_backend() -> bool:
    backend = settings.ARTIFACT_PERSISTENCE_BACKEND.lower()
    if backend != "db":
        return False

    # Safe fallback for local VS Code-only development.
    return bool(os.getenv("DATABASE_URL", "").strip())


def _to_schema(artifact) -> CampaignArtifactRead:
    artifact_id = getattr(artifact, "artifact_id", None)
    if artifact_id is None:
        artifact_id = str(artifact.id)

    return CampaignArtifactRead.model_validate(
        {
            "id": artifact_id,
            "campaign_id": artifact.campaign_id,
            "artifact_type": artifact.artifact_type.value,
            "title": artifact.title,
            "version": artifact.version,
            "status": artifact.status.value,
            "content": artifact.content,
            "author": artifact.author,
            "approver": artifact.approver,
            "approval_comment": artifact.approval_comment,
            "created_at": artifact.created_at,
            "updated_at": artifact.updated_at,
        }
    )


@router.post("/{campaign_id}/generate", response_model=CampaignArtifactRead)
async def generate_artifact(
    campaign_id: int,
    payload: ArtifactGenerationRequest,
    _: object = Depends(require_permissions(["campaign.artifacts.write"])),
    db: AsyncSession = Depends(get_db),
) -> CampaignArtifactRead:
    if _use_db_backend():
        service = CampaignArtifactDbService(db)
        generated = await service.generate_artifact(
            campaign_id=campaign_id,
            artifact_type=_to_db_service_type(payload.artifact_type),
            content=payload.content,
            author=payload.author,
        )
        return _to_schema(generated)

    artifact_type = _to_service_type(payload.artifact_type)
    generated = artifact_service.generate_artifact(campaign_id, artifact_type, payload.content, payload.author)
    return _to_schema(generated)


@router.post("/{campaign_id}/generate/all", response_model=list[CampaignArtifactRead])
async def generate_all_artifacts(
    campaign_id: int,
    payload: ArtifactBulkGenerationRequest,
    _: object = Depends(require_permissions(["campaign.artifacts.write"])),
    db: AsyncSession = Depends(get_db),
) -> list[CampaignArtifactRead]:
    generated = []
    for artifact_type in CampaignArtifactType:
        request_payload = payload.content_by_type.get(artifact_type, {})
        generated_payload = ArtifactGenerationRequest(
            artifact_type=artifact_type,
            content=request_payload,
            author=payload.author,
        )
        generated.append(await generate_artifact(campaign_id, generated_payload, db=db))
    return generated


@router.get("/{campaign_id}/{artifact_type}/versions", response_model=list[CampaignArtifactRead])
async def list_artifact_versions(
    campaign_id: int,
    artifact_type: CampaignArtifactType,
    _: object = Depends(require_permissions(["campaign.artifacts.read"])),
    db: AsyncSession = Depends(get_db),
) -> list[CampaignArtifactRead]:
    if _use_db_backend():
        service = CampaignArtifactDbService(db)
        versions = await service.list_versions(campaign_id, _to_db_service_type(artifact_type))
        return [_to_schema(item) for item in versions]

    versions = artifact_service.list_versions(campaign_id, _to_service_type(artifact_type))
    return [_to_schema(item) for item in versions]


@router.get("/{campaign_id}/{artifact_type}/current", response_model=CampaignArtifactRead)
async def get_current_version(
    campaign_id: int,
    artifact_type: CampaignArtifactType,
    _: object = Depends(require_permissions(["campaign.artifacts.read"])),
    db: AsyncSession = Depends(get_db),
) -> CampaignArtifactRead:
    if _use_db_backend():
        service = CampaignArtifactDbService(db)
        current = await service.get_current(campaign_id, _to_db_service_type(artifact_type))
    else:
        current = artifact_service.get_current_version(campaign_id, _to_service_type(artifact_type))

    if current is None:
        raise HTTPException(status_code=404, detail="Current artifact version not found.")
    return _to_schema(current)


@router.post("/{campaign_id}/{artifact_type}/approval/submit", response_model=CampaignArtifactRead)
async def submit_for_approval(
    campaign_id: int,
    artifact_type: CampaignArtifactType,
    _: object = Depends(require_permissions(["campaign.artifacts.approve"])),
    db: AsyncSession = Depends(get_db),
) -> CampaignArtifactRead:
    try:
        if _use_db_backend():
            service = CampaignArtifactDbService(db)
            artifact = await service.submit_for_approval(campaign_id, _to_db_service_type(artifact_type))
        else:
            artifact = artifact_service.submit_for_approval(campaign_id, _to_service_type(artifact_type))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_schema(artifact)


@router.post("/{campaign_id}/{artifact_type}/approval/review", response_model=CampaignArtifactRead)
async def review_artifact(
    campaign_id: int,
    artifact_type: CampaignArtifactType,
    payload: ArtifactReviewDecision,
    _: object = Depends(require_permissions(["campaign.artifacts.approve"])),
    db: AsyncSession = Depends(get_db),
) -> CampaignArtifactRead:
    try:
        if _use_db_backend():
            service = CampaignArtifactDbService(db)
            artifact = await service.review_approval(
                campaign_id=campaign_id,
                artifact_type=_to_db_service_type(artifact_type),
                reviewer=payload.reviewer,
                approve=payload.approve,
                comment=payload.comment,
            )
        else:
            artifact = artifact_service.review_approval(
                campaign_id=campaign_id,
                artifact_type=_to_service_type(artifact_type),
                reviewer=payload.reviewer,
                approve=payload.approve,
                comment=payload.comment,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_schema(artifact)


@router.post("/{campaign_id}/{artifact_type}/rollback", response_model=CampaignArtifactRead)
async def rollback_artifact(
    campaign_id: int,
    artifact_type: CampaignArtifactType,
    payload: ArtifactRollbackRequest,
    _: object = Depends(require_permissions(["campaign.artifacts.write"])),
    db: AsyncSession = Depends(get_db),
) -> CampaignArtifactRead:
    try:
        if _use_db_backend():
            service = CampaignArtifactDbService(db)
            artifact = await service.rollback_to_version(
                campaign_id=campaign_id,
                artifact_type=_to_db_service_type(artifact_type),
                target_version=payload.target_version,
                actor=payload.actor,
            )
        else:
            artifact = artifact_service.rollback_to_version(
                campaign_id=campaign_id,
                artifact_type=_to_service_type(artifact_type),
                target_version=payload.target_version,
                actor=payload.actor,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_schema(artifact)


@router.post("/{campaign_id}/exports/excel", response_model=ArtifactExportResponse)
async def export_excel(
    campaign_id: int,
    _: object = Depends(require_permissions(["campaign.artifacts.export"])),
    db: AsyncSession = Depends(get_db),
) -> ArtifactExportResponse:
    if _use_db_backend():
        service = CampaignArtifactDbService(db)
        path = await service.export_excel(campaign_id)
    else:
        path = artifact_service.export_excel(campaign_id)
    return ArtifactExportResponse(format="excel", path=str(path))


@router.post("/{campaign_id}/exports/word", response_model=ArtifactExportResponse)
async def export_word(
    campaign_id: int,
    _: object = Depends(require_permissions(["campaign.artifacts.export"])),
    db: AsyncSession = Depends(get_db),
) -> ArtifactExportResponse:
    if _use_db_backend():
        service = CampaignArtifactDbService(db)
        path = await service.export_word(campaign_id)
    else:
        path = artifact_service.export_word(campaign_id)
    return ArtifactExportResponse(format="word", path=str(path))
