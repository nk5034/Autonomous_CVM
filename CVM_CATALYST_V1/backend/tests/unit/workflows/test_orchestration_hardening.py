"""Security and integrity tests for orchestration hardening changes."""

from __future__ import annotations

import pytest

from src.workflows.orchestration.persistence import WorkflowCheckpointStore, WorkflowStateStore
from src.workflows.orchestration.service import CampaignWorkflowOrchestrator
from src.workflows.orchestration.state import CampaignState, WorkflowNode, WorkflowRunStatus


def test_state_store_rejects_path_traversal_workflow_id(tmp_path) -> None:
    store = WorkflowStateStore(base_dir=tmp_path)
    state = CampaignState(campaign_id=1, workflow_id="../bad", thread_id="thread-1")

    with pytest.raises(ValueError, match="Invalid workflow_id"):
        store.save_state(state)


def test_checkpoint_store_rejects_invalid_checkpoint_id(tmp_path) -> None:
    store = WorkflowCheckpointStore(base_dir=tmp_path)

    with pytest.raises(ValueError, match="Invalid checkpoint_id"):
        store.load_checkpoint("wf-1", "../checkpoint")


def test_mark_node_completed_updates_status() -> None:
    state = CampaignState(
        campaign_id=100,
        workflow_id="wf-100",
        thread_id="thread-100",
        status=WorkflowRunStatus.RUNNING,
    )
    state.mark_node_started(WorkflowNode.BRIEFING_INTAKE)
    state.mark_node_completed(WorkflowNode.BRIEFING_INTAKE, {"ok": True})

    latest = state.execution_history[-1]
    assert latest.node == WorkflowNode.BRIEFING_INTAKE
    assert latest.status == WorkflowRunStatus.COMPLETED
    assert latest.completed_at is not None


def test_approve_requires_pending_approval(tmp_path) -> None:
    state_store = WorkflowStateStore(base_dir=tmp_path / "states")
    checkpoint_store = WorkflowCheckpointStore(base_dir=tmp_path / "checkpoints")
    orchestrator = CampaignWorkflowOrchestrator(
        state_store=state_store,
        checkpoint_store=checkpoint_store,
    )

    state = CampaignState(
        campaign_id=200,
        workflow_id="wf-200",
        thread_id="thread-200",
        status=WorkflowRunStatus.RUNNING,
        awaiting_approval=False,
        pending_approval_for=None,
    )
    state_store.save_state(state)

    with pytest.raises(ValueError, match="No pending approval"):
        orchestrator.approve(
            workflow_id="wf-200",
            approver="ops_user",
            decision="approved",
            comment="attempted without pending gate",
        )
