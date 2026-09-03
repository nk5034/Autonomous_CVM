"""Domain SQLAlchemy entities for CVM Catalyst."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


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


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    approvals: Mapped[list[Approval]] = relationship(back_populates="approver")
    audit_events: Mapped[list[AuditLog]] = relationship(back_populates="actor")


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Permission(BaseModel):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SelectionBriefing(BaseModel):
    __tablename__ = "selection_briefings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign | None] = relationship(back_populates="selection_briefing", uselist=False)


class Campaign(BaseModel):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[CampaignStatus] = mapped_column(
        SAEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False
    )
    selection_briefing_id: Mapped[int | None] = mapped_column(
        ForeignKey("selection_briefings.id"), nullable=True
    )

    selection_briefing: Mapped[SelectionBriefing | None] = relationship(back_populates="campaign")
    configurations: Mapped[list[CampaignConfiguration]] = relationship(back_populates="campaign")
    audiences: Mapped[list[AudienceDefinition]] = relationship(back_populates="campaign")
    tests: Mapped[list[TestCase]] = relationship(back_populates="campaign")
    simulations: Mapped[list[Simulation]] = relationship(back_populates="campaign")
    ab_tests: Mapped[list[ABTest]] = relationship(back_populates="campaign")
    approvals: Mapped[list[Approval]] = relationship(back_populates="campaign")
    deployments: Mapped[list[Deployment]] = relationship(back_populates="campaign")
    workflows: Mapped[list[Workflow]] = relationship(back_populates="campaign")
    artifacts: Mapped[list[CampaignArtifact]] = relationship(back_populates="campaign")


class CampaignConfiguration(BaseModel):
    __tablename__ = "campaign_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    config_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="configurations")


class AudienceDefinition(BaseModel):
    __tablename__ = "audience_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="audiences")


class TestCase(BaseModel):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    expected_output: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="tests")


class Simulation(BaseModel):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    result_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="simulations")


class ABTest(BaseModel):
    __tablename__ = "ab_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    variant_a: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    variant_b: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="ab_tests")


class Approval(BaseModel):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="approvals")
    approver: Mapped[User] = relationship(back_populates="approvals")


class Deployment(BaseModel):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    status: Mapped[DeploymentStatus] = mapped_column(
        SAEnum(DeploymentStatus), default=DeploymentStatus.PLANNED, nullable=False
    )
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="deployments")


class CampaignArtifact(BaseModel):
    __tablename__ = "campaign_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    artifact_type: Mapped[CampaignArtifactType] = mapped_column(SAEnum(CampaignArtifactType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CampaignArtifactStatus] = mapped_column(
        SAEnum(CampaignArtifactStatus), default=CampaignArtifactStatus.DRAFT, nullable=False
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    approver: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approval_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="artifacts")
    approvals: Mapped[list[CampaignArtifactApproval]] = relationship(back_populates="artifact")

    @property
    def artifact_id(self) -> str:
        return str(self.id)


class CampaignArtifactApproval(BaseModel):
    __tablename__ = "campaign_artifact_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[int] = mapped_column(ForeignKey("campaign_artifacts.id"), nullable=False, index=True)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    artifact: Mapped[CampaignArtifact] = relationship(back_populates="approvals")


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    aggregate_name: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    actor: Mapped[User | None] = relationship(back_populates="audit_events")


class Workflow(BaseModel):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus), default=WorkflowStatus.CREATED, nullable=False
    )
    state_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="workflows")
