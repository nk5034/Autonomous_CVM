"""Domain services for orchestration of aggregate behaviors."""
from __future__ import annotations

from src.models.entities import (
    ABTest,
    Approval,
    ApprovalStatus,
    AuditLog,
    Campaign,
    CampaignStatus,
    Deployment,
    DeploymentStatus,
    Permission,
    Role,
    Simulation,
    Workflow,
    WorkflowStatus,
)
from src.repositories.interfaces import (
    ABTestRepository,
    ApprovalRepository,
    AuditLogRepository,
    CampaignRepository,
    DeploymentRepository,
    PermissionRepository,
    RoleRepository,
    SimulationRepository,
    WorkflowRepository,
)


class CampaignDomainService:
    """Coordinates campaign lifecycle transitions."""

    def __init__(self, campaign_repo: CampaignRepository, audit_repo: AuditLogRepository) -> None:
        self._campaign_repo = campaign_repo
        self._audit_repo = audit_repo

    async def configure_campaign(self, campaign_id: int, actor_user_id: int | None) -> Campaign | None:
        campaign = await self._campaign_repo.get_by_id(campaign_id)
        if campaign is None:
            return None
        campaign.status = CampaignStatus.CONFIGURED
        campaign = await self._campaign_repo.add(campaign)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Campaign",
                aggregate_id=str(campaign.id),
                event_type="campaign.configured",
                payload={"status": campaign.status.value},
            )
        )
        return campaign


class ApprovalDomainService:
    """Coordinates approval changes and audit capture."""

    def __init__(self, approval_repo: ApprovalRepository, audit_repo: AuditLogRepository) -> None:
        self._approval_repo = approval_repo
        self._audit_repo = audit_repo

    async def register_approval(self, approval: Approval, actor_user_id: int | None) -> Approval:
        saved = await self._approval_repo.add(approval)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Approval",
                aggregate_id=str(saved.id),
                event_type="approval.recorded",
                payload={"status": saved.status.value},
            )
        )
        return saved

    async def approve(self, approval: Approval, actor_user_id: int | None) -> Approval:
        approval.status = ApprovalStatus.APPROVED
        return await self.register_approval(approval, actor_user_id)


class DeploymentDomainService:
    """Coordinates deployment transitions and corresponding audit events."""

    def __init__(self, deployment_repo: DeploymentRepository, audit_repo: AuditLogRepository) -> None:
        self._deployment_repo = deployment_repo
        self._audit_repo = audit_repo

    async def mark_running(self, deployment: Deployment, actor_user_id: int | None) -> Deployment:
        deployment.status = DeploymentStatus.RUNNING
        saved = await self._deployment_repo.add(deployment)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Deployment",
                aggregate_id=str(saved.id),
                event_type="deployment.running",
                payload={"status": saved.status.value},
            )
        )
        return saved


class WorkflowDomainService:
    """Coordinates workflow status and persistence."""

    def __init__(self, workflow_repo: WorkflowRepository, audit_repo: AuditLogRepository) -> None:
        self._workflow_repo = workflow_repo
        self._audit_repo = audit_repo

    async def start(self, workflow: Workflow, actor_user_id: int | None) -> Workflow:
        workflow.status = WorkflowStatus.IN_PROGRESS
        saved = await self._workflow_repo.add(workflow)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Workflow",
                aggregate_id=str(saved.id),
                event_type="workflow.started",
                payload={"status": saved.status.value},
            )
        )
        return saved


class ExperimentationDomainService:
    """Coordinates test and simulation registration flows."""

    def __init__(
        self,
        ab_test_repo: ABTestRepository,
        simulation_repo: SimulationRepository,
        audit_repo: AuditLogRepository,
    ) -> None:
        self._ab_test_repo = ab_test_repo
        self._simulation_repo = simulation_repo
        self._audit_repo = audit_repo

    async def register_ab_test(self, ab_test: ABTest, actor_user_id: int | None) -> ABTest:
        saved = await self._ab_test_repo.add(ab_test)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="ABTest",
                aggregate_id=str(saved.id),
                event_type="ab_test.registered",
                payload={"campaign_id": saved.campaign_id},
            )
        )
        return saved

    async def register_simulation(self, simulation: Simulation, actor_user_id: int | None) -> Simulation:
        saved = await self._simulation_repo.add(simulation)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Simulation",
                aggregate_id=str(saved.id),
                event_type="simulation.registered",
                payload={"campaign_id": saved.campaign_id},
            )
        )
        return saved


class AccessControlDomainService:
    """Coordinates role and permission setup at domain layer."""

    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        audit_repo: AuditLogRepository,
    ) -> None:
        self._role_repo = role_repo
        self._permission_repo = permission_repo
        self._audit_repo = audit_repo

    async def register_role(self, role: Role, actor_user_id: int | None) -> Role:
        saved = await self._role_repo.add(role)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Role",
                aggregate_id=str(saved.id),
                event_type="role.registered",
                payload={"name": saved.name},
            )
        )
        return saved

    async def register_permission(self, permission: Permission, actor_user_id: int | None) -> Permission:
        saved = await self._permission_repo.add(permission)
        await self._audit_repo.add(
            AuditLog(
                actor_user_id=actor_user_id,
                aggregate_name="Permission",
                aggregate_id=str(saved.id),
                event_type="permission.registered",
                payload={"code": saved.code},
            )
        )
        return saved
