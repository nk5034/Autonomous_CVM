"""Pydantic state models for LangGraph campaign orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowNode(str, Enum):
    """Canonical workflow nodes for campaign orchestration."""

    BRIEFING_INTAKE = "briefing_intake"
    BRIEFING_AUTHOR = "briefing_author"
    BRIEFING_VALIDATION = "briefing_validation"
    AUDIENCE_DESIGN = "audience_design"
    CAMPAIGN_CONFIGURATION = "campaign_configuration"
    TEST_GENERATION = "test_generation"
    TEST_EXECUTION = "test_execution"
    TESTING_PLATFORM = "testing_platform"
    SIMULATION = "simulation"
    AB_TESTING = "ab_testing"
    BUSINESS_APPROVAL = "business_approval"
    DEPLOYMENT = "deployment"
    REPORTING = "reporting"


class WorkflowRunStatus(str, Enum):
    """Runtime status of a workflow run."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalDecision(str, Enum):
    """Human approval decision."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NodeExecutionRecord(BaseModel):
    """A single node execution trace record."""

    node: WorkflowNode
    started_at: datetime
    completed_at: datetime | None = None
    status: WorkflowRunStatus
    details: dict[str, Any] = Field(default_factory=dict)


class ManualOverrideRecord(BaseModel):
    """Records manual override actions for a specific node."""

    node: WorkflowNode
    actor: str
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    active: bool = True


class ApprovalRecord(BaseModel):
    """Records approval decisions for nodes requiring business sign-off."""

    node: WorkflowNode
    approver: str
    decision: ApprovalDecision
    comment: str | None = None
    decided_at: datetime


class CampaignState(BaseModel):
    """Workflow state persisted and exchanged across LangGraph nodes."""

    campaign_id: int
    workflow_id: str
    thread_id: str
    status: WorkflowRunStatus = WorkflowRunStatus.CREATED
    current_node: WorkflowNode | None = None
    next_node: WorkflowNode | None = None
    paused: bool = False
    pause_reason: str | None = None
    awaiting_approval: bool = False
    pending_approval_for: WorkflowNode | None = None
    approvals: dict[str, ApprovalRecord] = Field(default_factory=dict)
    manual_overrides: dict[str, ManualOverrideRecord] = Field(default_factory=dict)
    artifacts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    execution_history: list[NodeExecutionRecord] = Field(default_factory=list)
    checkpoint_ids: list[str] = Field(default_factory=list)
    audit_events: list[dict[str, Any]] = Field(default_factory=list)
    last_error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def mark_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        """Append an auditable event entry."""
        self.audit_events.append(
            {
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": payload or {},
            }
        )
        self._touch()

    def mark_node_started(self, node: WorkflowNode) -> None:
        """Mark a node as started and add execution trace."""
        self.current_node = node
        self.status = WorkflowRunStatus.RUNNING
        self.execution_history.append(
            NodeExecutionRecord(
                node=node,
                started_at=datetime.now(timezone.utc),
                status=WorkflowRunStatus.RUNNING,
            )
        )
        self.mark_event("node.started", {"node": node.value})

    def mark_node_completed(
        self,
        node: WorkflowNode,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Mark node completion and annotate details."""
        completed_at = datetime.now(timezone.utc)
        matched_record = False
        for record in reversed(self.execution_history):
            if record.node == node and record.completed_at is None:
                record.completed_at = completed_at
                record.details = details or {}
                record.status = WorkflowRunStatus.COMPLETED
                matched_record = True
                break
        if not matched_record:
            self.execution_history.append(
                NodeExecutionRecord(
                    node=node,
                    started_at=completed_at,
                    completed_at=completed_at,
                    status=WorkflowRunStatus.COMPLETED,
                    details=details or {},
                )
            )
        self.mark_event(
            "node.completed",
            {"node": node.value, "details": details or {}},
        )

    def set_next_node(self, node: WorkflowNode | None) -> None:
        """Set the next node for execution."""
        self.next_node = node
        if node is None and self.status not in {
            WorkflowRunStatus.FAILED,
            WorkflowRunStatus.PAUSED,
            WorkflowRunStatus.WAITING_APPROVAL,
        }:
            self.status = WorkflowRunStatus.COMPLETED
        self.mark_event("node.next", {"next_node": node.value if node else None})

    def should_pause(self) -> bool:
        """Return True when workflow execution should pause."""
        return self.paused

    def to_dict(self) -> dict[str, Any]:
        """Serialize state for persistence and graph invocation."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CampaignState":
        """Hydrate state from persisted dictionary."""
        return cls.model_validate(data)


ORDERED_NODES: list[WorkflowNode] = [
    WorkflowNode.BRIEFING_INTAKE,
    WorkflowNode.BRIEFING_AUTHOR,
    WorkflowNode.BRIEFING_VALIDATION,
    WorkflowNode.AUDIENCE_DESIGN,
    WorkflowNode.CAMPAIGN_CONFIGURATION,
    WorkflowNode.TEST_GENERATION,
    WorkflowNode.TEST_EXECUTION,
    WorkflowNode.TESTING_PLATFORM,
    WorkflowNode.SIMULATION,
    WorkflowNode.AB_TESTING,
    WorkflowNode.BUSINESS_APPROVAL,
    WorkflowNode.DEPLOYMENT,
    WorkflowNode.REPORTING,
]
