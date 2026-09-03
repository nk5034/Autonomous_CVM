"""Service layer for running and controlling LangGraph campaign orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any

from src.workflows.orchestration.graph import build_initial_state, compile_campaign_graph
from src.workflows.orchestration.persistence import WorkflowCheckpointStore, WorkflowStateStore
from src.workflows.orchestration.state import (
    ApprovalDecision,
    ApprovalRecord,
    CampaignState,
    ManualOverrideRecord,
    WorkflowNode,
    WorkflowRunStatus,
)
from src.workflows.orchestration.visualization import mermaid_workflow_diagram
from src.workflows.observability.langsmith import get_langsmith_tracker


class CampaignWorkflowOrchestrator:
    """High-level API for start/resume/pause/approval/override workflow controls."""

    def __init__(
        self,
        state_store: WorkflowStateStore | None = None,
        checkpoint_store: WorkflowCheckpointStore | None = None,
        graph: Any | None = None,
    ) -> None:
        self.state_store = state_store or WorkflowStateStore()
        self.checkpoint_store = checkpoint_store or WorkflowCheckpointStore()
        self.graph = graph or compile_campaign_graph()
        self._langsmith = get_langsmith_tracker()

    def _persist_and_checkpoint(self, state: CampaignState, label: str) -> CampaignState:
        checkpoint_id = self.checkpoint_store.create_checkpoint(state, label=label)
        state.mark_event("checkpoint.created", {"checkpoint_id": checkpoint_id, "label": label})
        self.state_store.save_state(state)
        return state

    def _invoke_graph(self, state: CampaignState) -> CampaignState:
        started_at = time.perf_counter()
        state.status = WorkflowRunStatus.RUNNING
        try:
            result = self.graph.invoke(state.to_dict())
            new_state = CampaignState.from_dict(result)
            self._langsmith.track_workflow_execution(
                workflow_id=state.workflow_id,
                campaign_id=state.campaign_id,
                event_name="workflow.graph.invoke",
                status=new_state.status.value,
                latency_ms=(time.perf_counter() - started_at) * 1000,
                input_data={"status": state.status.value, "next_node": state.next_node.value if state.next_node else None},
                output_data={
                    "status": new_state.status.value,
                    "current_node": new_state.current_node.value if new_state.current_node else None,
                    "next_node": new_state.next_node.value if new_state.next_node else None,
                },
            )
            return new_state
        except Exception as exc:
            self._langsmith.track_workflow_execution(
                workflow_id=state.workflow_id,
                campaign_id=state.campaign_id,
                event_name="workflow.graph.invoke",
                status="failed",
                latency_ms=(time.perf_counter() - started_at) * 1000,
                input_data={"status": state.status.value, "next_node": state.next_node.value if state.next_node else None},
                output_data={},
                error_message=str(exc),
            )
            raise

    def start(self, campaign_id: int, workflow_id: str) -> CampaignState:
        started_at = time.perf_counter()
        state = build_initial_state(campaign_id=campaign_id, workflow_id=workflow_id)
        state.mark_event("workflow.started", {"campaign_id": campaign_id})
        state = self._invoke_graph(state)
        self._langsmith.track_workflow_execution(
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            event_name="workflow.start",
            status=state.status.value,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            input_data={"campaign_id": campaign_id},
            output_data={"status": state.status.value, "next_node": state.next_node.value if state.next_node else None},
        )
        return self._persist_and_checkpoint(state, label="start")

    def resume(self, workflow_id: str) -> CampaignState:
        started_at = time.perf_counter()
        state = self.state_store.load_state(workflow_id)
        if state is None:
            raise ValueError(f"Workflow state not found for workflow_id='{workflow_id}'.")
        state.paused = False
        state.pause_reason = None
        if state.status in {WorkflowRunStatus.PAUSED, WorkflowRunStatus.WAITING_APPROVAL}:
            state.status = WorkflowRunStatus.RUNNING
        state.mark_event("workflow.resumed", {})
        state = self._invoke_graph(state)
        self._langsmith.track_workflow_execution(
            workflow_id=workflow_id,
            campaign_id=state.campaign_id,
            event_name="workflow.resume",
            status=state.status.value,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            input_data={},
            output_data={"status": state.status.value, "next_node": state.next_node.value if state.next_node else None},
        )
        return self._persist_and_checkpoint(state, label="resume")

    def pause(self, workflow_id: str, reason: str) -> CampaignState | None:
        started_at = time.perf_counter()
        state = self.state_store.load_state(workflow_id)
        if state is None:
            return None
        state.paused = True
        state.pause_reason = reason
        state.status = WorkflowRunStatus.PAUSED
        state.mark_event("workflow.paused", {"reason": reason})
        self._langsmith.track_workflow_execution(
            workflow_id=workflow_id,
            campaign_id=state.campaign_id,
            event_name="workflow.pause",
            status=state.status.value,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            input_data={"reason": reason},
            output_data={"status": state.status.value},
        )
        return self._persist_and_checkpoint(state, label="pause")

    def approve(
        self,
        workflow_id: str,
        approver: str,
        decision: str,
        comment: str | None = None,
    ) -> CampaignState | None:
        started_at = time.perf_counter()
        state = self.state_store.load_state(workflow_id)
        if state is None:
            return None

        try:
            enum_decision = ApprovalDecision(decision)
        except ValueError as exc:
            raise ValueError(
                "decision must be one of: pending, approved, rejected"
            ) from exc

        if (
            enum_decision in {ApprovalDecision.APPROVED, ApprovalDecision.REJECTED}
            and not state.awaiting_approval
        ):
            raise ValueError(
                "No pending approval exists for this workflow. Resume the workflow until approval is requested."
            )

        approval_node = state.pending_approval_for or WorkflowNode.BUSINESS_APPROVAL
        state.approvals[approval_node.value] = ApprovalRecord(
            node=approval_node,
            approver=approver,
            decision=enum_decision,
            comment=comment,
            decided_at=datetime.now(timezone.utc),
        )
        state.mark_event(
            "workflow.approval_recorded",
            {
                "node": approval_node.value,
                "approver": approver,
                "decision": enum_decision.value,
            },
        )

        if enum_decision == ApprovalDecision.APPROVED:
            state.awaiting_approval = False
            state.pending_approval_for = None
            state.status = WorkflowRunStatus.RUNNING
            state = self._invoke_graph(state)
        elif enum_decision == ApprovalDecision.REJECTED:
            state.awaiting_approval = False
            state.pending_approval_for = None
            state.status = WorkflowRunStatus.FAILED
            state.last_error = "Business approval rejected."

        self._langsmith.track_approval_flow(
            workflow_id=workflow_id,
            campaign_id=state.campaign_id,
            node_name=approval_node.value,
            decision=enum_decision.value,
            approver=approver,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            comment=comment,
            error_message=state.last_error,
        )

        return self._persist_and_checkpoint(state, label=f"approval-{enum_decision.value}")

    def apply_manual_override(
        self,
        workflow_id: str,
        node: str,
        actor: str,
        reason: str,
        payload: dict[str, Any],
    ) -> CampaignState | None:
        started_at = time.perf_counter()
        state = self.state_store.load_state(workflow_id)
        if state is None:
            return None

        try:
            target_node = WorkflowNode(node)
        except ValueError as exc:
            valid_values = ", ".join(item.value for item in WorkflowNode)
            raise ValueError(f"Invalid node '{node}'. Expected one of: {valid_values}") from exc

        record = ManualOverrideRecord(
            node=target_node,
            actor=actor,
            reason=reason,
            payload=payload,
            created_at=datetime.now(timezone.utc),
            active=True,
        )
        state.manual_overrides[target_node.value] = record
        state.artifacts[target_node.value] = {
            "artifact": f"{target_node.value}_manual_override",
            "source": "manual_override",
            "payload": payload,
            "actor": actor,
            "reason": reason,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_event(
            "workflow.manual_override",
            {
                "node": target_node.value,
                "actor": actor,
                "reason": reason,
            },
        )
        self._langsmith.track_workflow_execution(
            workflow_id=workflow_id,
            campaign_id=state.campaign_id,
            event_name="workflow.manual_override",
            status=state.status.value,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            input_data={"node": node, "actor": actor, "reason": reason},
            output_data={"override_active": True},
            metadata={"flow": "manual_override"},
        )
        return self._persist_and_checkpoint(state, label=f"override-{target_node.value}")

    def get_state(self, workflow_id: str) -> CampaignState | None:
        return self.state_store.load_state(workflow_id)

    def export_mermaid(self) -> str:
        try:
            graph_view = self.graph.get_graph()
            draw_mermaid = getattr(graph_view, "draw_mermaid", None)
            if callable(draw_mermaid):
                return draw_mermaid()
        except Exception:
            pass
        return mermaid_workflow_diagram()

