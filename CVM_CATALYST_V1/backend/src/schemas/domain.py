"""Pydantic schemas for Phase 2 domain model."""
from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    CONFIGURED = "configured"
    SCHEDULED = "scheduled"
    DEPLOYED = "deployed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DeploymentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class WorkflowStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    DONE = "done"
    FAILED = "failed"


class CampaignArtifactType(str, Enum):
    SELECTION_BRIEFING = "selection_briefing"
    AUDIENCE_DEFINITION = "audience_definition"
    CAMPAIGN_CONFIGURATION = "campaign_configuration"
    PROPOSITION_SHEET = "proposition_sheet"
    TREATMENT_SHEET = "treatment_sheet"
    CONTACT_RULES = "contact_rules"
    VOLUME_CONSTRAINTS = "volume_constraints"
    CONTROL_GROUP_DEFINITION = "control_group_definition"
    REPORTING_CONFIGURATION = "reporting_configuration"


class CampaignArtifactStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


class EntitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampsMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserCreate(BaseModel):
    email: str
    display_name: str


class UserRead(EntitySchema, TimestampsMixin):
    id: int
    email: str
    display_name: str
    is_active: bool


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleRead(EntitySchema, TimestampsMixin):
    id: int
    name: str
    description: str | None


class PermissionCreate(BaseModel):
    code: str
    description: str | None = None


class PermissionRead(EntitySchema, TimestampsMixin):
    id: int
    code: str
    description: str | None


class SelectionBriefingCreate(BaseModel):
    title: str
    objective: str | None = None
    content: dict = Field(default_factory=dict)


class SelectionBriefingRead(EntitySchema, TimestampsMixin):
    id: int
    title: str
    objective: str | None
    content: dict


class CampaignCreate(BaseModel):
    name: str
    selection_briefing_id: int | None = None


class CampaignRead(EntitySchema, TimestampsMixin):
    id: int
    name: str
    status: CampaignStatus
    selection_briefing_id: int | None


class CampaignConfigurationCreate(BaseModel):
    campaign_id: int
    config_version: int = 1
    parameters: dict = Field(default_factory=dict)


class CampaignConfigurationRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    config_version: int
    parameters: dict


class AudienceDefinitionCreate(BaseModel):
    campaign_id: int
    name: str
    criteria: dict = Field(default_factory=dict)


class AudienceDefinitionRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    name: str
    criteria: dict


class TestCaseCreate(BaseModel):
    campaign_id: int
    name: str
    input_payload: dict = Field(default_factory=dict)
    expected_output: dict = Field(default_factory=dict)


class TestCaseRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    name: str
    input_payload: dict
    expected_output: dict


class SimulationCreate(BaseModel):
    campaign_id: int
    name: str
    result_summary: dict = Field(default_factory=dict)


class SimulationRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    name: str
    result_summary: dict


class ABTestCreate(BaseModel):
    campaign_id: int
    hypothesis: str
    variant_a: dict = Field(default_factory=dict)
    variant_b: dict = Field(default_factory=dict)


class ABTestRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    hypothesis: str
    variant_a: dict
    variant_b: dict


class ApprovalCreate(BaseModel):
    campaign_id: int
    approver_id: int
    status: ApprovalStatus = ApprovalStatus.PENDING
    comment: str | None = None


class ApprovalRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    approver_id: int
    status: ApprovalStatus
    comment: str | None


class DeploymentCreate(BaseModel):
    campaign_id: int
    status: DeploymentStatus = DeploymentStatus.PLANNED


class DeploymentRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    status: DeploymentStatus
    deployed_at: datetime | None


class AuditLogCreate(BaseModel):
    actor_user_id: int | None = None
    aggregate_name: str
    aggregate_id: str
    event_type: str
    payload: dict = Field(default_factory=dict)


class AuditLogRead(EntitySchema, TimestampsMixin):
    id: int
    actor_user_id: int | None
    aggregate_name: str
    aggregate_id: str
    event_type: str
    payload: dict


class WorkflowCreate(BaseModel):
    campaign_id: int
    name: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    state_snapshot: dict = Field(default_factory=dict)


class WorkflowRead(EntitySchema, TimestampsMixin):
    id: int
    campaign_id: int
    name: str
    status: WorkflowStatus
    state_snapshot: dict


class CampaignArtifactCreate(BaseModel):
    campaign_id: int
    artifact_type: CampaignArtifactType
    title: str
    content: dict = Field(default_factory=dict)
    author: str


class CampaignArtifactRead(EntitySchema, TimestampsMixin):
    id: str
    campaign_id: int
    artifact_type: CampaignArtifactType
    title: str
    version: int
    status: CampaignArtifactStatus
    content: dict
    author: str
    approver: str | None = None
    approval_comment: str | None = None


class ArtifactApprovalRequest(BaseModel):
    reviewer: str
    comment: str | None = None


class ArtifactReviewDecision(BaseModel):
    reviewer: str
    approve: bool
    comment: str | None = None


class ArtifactGenerationRequest(BaseModel):
    artifact_type: CampaignArtifactType
    content: dict = Field(default_factory=dict)
    author: str


class ArtifactBulkGenerationRequest(BaseModel):
    author: str
    content_by_type: dict[CampaignArtifactType, dict] = Field(default_factory=dict)


class ArtifactRollbackRequest(BaseModel):
    target_version: int
    actor: str


class ArtifactExportResponse(BaseModel):
    format: str
    path: str


class Phase7TestingPlatformSummary(BaseModel):
    status: str | None = None
    execution_summary: dict = Field(default_factory=dict)
    report_summary: dict = Field(default_factory=dict)
    audit_event_count: int = 0

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "execution_summary": {
                    "total": 12,
                    "passed": 11,
                    "failed": 1,
                    "pass_rate": 91.67,
                    "started_at": "2026-09-01T09:30:00Z",
                    "completed_at": "2026-09-01T09:30:04Z",
                },
                "report_summary": {
                    "run_id": "run_1788245404",
                    "total_tests": 12,
                    "passed_tests": 11,
                    "failed_tests": 1,
                    "pass_rate": 91.67,
                },
                "audit_event_count": 5,
            }
        }
    )


class WorkflowStartRequest(BaseModel):
    campaign_id: int
    workflow_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "campaign_id": 12001,
                "workflow_id": "wf_phase7_12001",
            }
        }
    )


class WorkflowApprovalRequest(BaseModel):
    approver: str
    decision: str
    comment: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "approver": "ops_user",
                "decision": "approved",
                "comment": "Approved after QA checks.",
            }
        }
    )


class WorkflowRunResponse(BaseModel):
    workflow_id: str
    campaign_id: int
    status: str
    current_node: str | None = None
    next_node: str | None = None
    awaiting_approval: bool = False
    last_error: str | None = None
    phase7_testing_platform: Phase7TestingPlatformSummary | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_phase7_12001",
                "campaign_id": 12001,
                "status": "running",
                "current_node": "testing_platform",
                "next_node": "simulation",
                "awaiting_approval": False,
                "last_error": None,
                "phase7_testing_platform": {
                    "status": "success",
                    "execution_summary": {
                        "total": 12,
                        "passed": 11,
                        "failed": 1,
                        "pass_rate": 91.67,
                    },
                    "report_summary": {
                        "total_tests": 12,
                        "passed_tests": 11,
                        "failed_tests": 1,
                        "pass_rate": 91.67,
                    },
                    "audit_event_count": 5,
                },
            }
        }
    )
