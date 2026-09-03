"""SQLAlchemy repositories for campaign artifact persistence."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.entities import (
    CampaignArtifact,
    CampaignArtifactApproval,
    CampaignArtifactType,
)
from src.repositories.interfaces import (
    CampaignArtifactApprovalRepository,
    CampaignArtifactRepository,
)


class SqlAlchemyCampaignArtifactRepository(CampaignArtifactRepository):
    """Database persistence for campaign artifact versions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, artifact: CampaignArtifact) -> CampaignArtifact:
        self._session.add(artifact)
        await self._session.flush()
        return artifact

    async def save(self, artifact: CampaignArtifact) -> CampaignArtifact:
        self._session.add(artifact)
        await self._session.flush()
        return artifact

    async def next_version(self, campaign_id: int, artifact_type: CampaignArtifactType) -> int:
        stmt = select(func.max(CampaignArtifact.version)).where(
            CampaignArtifact.campaign_id == campaign_id,
            CampaignArtifact.artifact_type == artifact_type,
        )
        current = await self._session.scalar(stmt)
        return (current or 0) + 1

    async def get_current(
        self,
        campaign_id: int,
        artifact_type: CampaignArtifactType,
    ) -> CampaignArtifact | None:
        stmt = (
            select(CampaignArtifact)
            .where(
                CampaignArtifact.campaign_id == campaign_id,
                CampaignArtifact.artifact_type == artifact_type,
            )
            .order_by(CampaignArtifact.version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_versions(
        self,
        campaign_id: int,
        artifact_type: CampaignArtifactType,
    ) -> list[CampaignArtifact]:
        stmt = (
            select(CampaignArtifact)
            .where(
                CampaignArtifact.campaign_id == campaign_id,
                CampaignArtifact.artifact_type == artifact_type,
            )
            .order_by(CampaignArtifact.version.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class SqlAlchemyCampaignArtifactApprovalRepository(CampaignArtifactApprovalRepository):
    """Database persistence for campaign artifact approval decisions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, approval: CampaignArtifactApproval) -> CampaignArtifactApproval:
        self._session.add(approval)
        await self._session.flush()
        return approval
