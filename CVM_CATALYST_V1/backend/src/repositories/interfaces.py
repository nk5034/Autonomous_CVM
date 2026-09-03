"""DDD repository interfaces for domain aggregates."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.entities import (
    ABTest,
    Approval,
    AudienceDefinition,
    AuditLog,
    Campaign,
    CampaignArtifact,
    CampaignArtifactApproval,
    CampaignArtifactStatus,
    CampaignArtifactType,
    CampaignConfiguration,
    Deployment,
    Permission,
    Role,
    SelectionBriefing,
    Simulation,
    TestCase,
    User,
    Workflow,
)


class Repository(ABC):
    """Marker base repository for DDD interfaces."""


class CampaignRepository(Repository):
    @abstractmethod
    async def add(self, campaign: Campaign) -> Campaign: ...

    @abstractmethod
    async def get_by_id(self, campaign_id: int) -> Campaign | None: ...

    @abstractmethod
    async def list_all(self) -> list[Campaign]: ...


class SelectionBriefingRepository(Repository):
    @abstractmethod
    async def add(self, briefing: SelectionBriefing) -> SelectionBriefing: ...

    @abstractmethod
    async def get_by_id(self, briefing_id: int) -> SelectionBriefing | None: ...


class CampaignConfigurationRepository(Repository):
    @abstractmethod
    async def add(self, configuration: CampaignConfiguration) -> CampaignConfiguration: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[CampaignConfiguration]: ...


class AudienceDefinitionRepository(Repository):
    @abstractmethod
    async def add(self, audience: AudienceDefinition) -> AudienceDefinition: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[AudienceDefinition]: ...


class TestCaseRepository(Repository):
    @abstractmethod
    async def add(self, test_case: TestCase) -> TestCase: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[TestCase]: ...


class SimulationRepository(Repository):
    @abstractmethod
    async def add(self, simulation: Simulation) -> Simulation: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[Simulation]: ...


class ABTestRepository(Repository):
    @abstractmethod
    async def add(self, ab_test: ABTest) -> ABTest: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[ABTest]: ...


class ApprovalRepository(Repository):
    @abstractmethod
    async def add(self, approval: Approval) -> Approval: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[Approval]: ...


class DeploymentRepository(Repository):
    @abstractmethod
    async def add(self, deployment: Deployment) -> Deployment: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[Deployment]: ...


class AuditLogRepository(Repository):
    @abstractmethod
    async def add(self, event: AuditLog) -> AuditLog: ...

    @abstractmethod
    async def list_by_aggregate(self, aggregate_name: str, aggregate_id: str) -> list[AuditLog]: ...


class UserRepository(Repository):
    @abstractmethod
    async def add(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...


class RoleRepository(Repository):
    @abstractmethod
    async def add(self, role: Role) -> Role: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None: ...


class PermissionRepository(Repository):
    @abstractmethod
    async def add(self, permission: Permission) -> Permission: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Permission | None: ...


class WorkflowRepository(Repository):
    @abstractmethod
    async def add(self, workflow: Workflow) -> Workflow: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: int) -> list[Workflow]: ...


class CampaignArtifactRepository(Repository):
    @abstractmethod
    async def create(self, artifact: CampaignArtifact) -> CampaignArtifact: ...

    @abstractmethod
    async def list_versions(self, campaign_id: int, artifact_type: CampaignArtifactType) -> list[CampaignArtifact]: ...

    @abstractmethod
    async def get_current(self, campaign_id: int, artifact_type: CampaignArtifactType) -> CampaignArtifact | None: ...

    @abstractmethod
    async def next_version(self, campaign_id: int, artifact_type: CampaignArtifactType) -> int: ...

    @abstractmethod
    async def save(self, artifact: CampaignArtifact) -> CampaignArtifact: ...


class CampaignArtifactApprovalRepository(Repository):
    @abstractmethod
    async def add(self, approval: CampaignArtifactApproval) -> CampaignArtifactApproval: ...
