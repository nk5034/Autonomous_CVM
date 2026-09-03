"""Deterministic LangGraph nodes for campaign orchestration."""
from __future__ import annotations

import atexit
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import time
from typing import Any, Callable

from src.services.artifact_generation import ArtifactType, CampaignArtifactService
from src.workflows.agents.base import AgentInput
from src.workflows.agents.testing import AutomatedTestExecutionFramework
from src.workflows.orchestration.state import (
    ApprovalDecision,
    CampaignState,
    ORDERED_NODES,
    WorkflowNode,
    WorkflowRunStatus,
)
from src.workflows.observability.langsmith import get_langsmith_tracker

NodeFunc = Callable[[dict[str, Any]], dict[str, Any]]
artifact_service = CampaignArtifactService()
langsmith_tracker = get_langsmith_tracker()
_ASYNC_BRIDGE_EXECUTOR = ThreadPoolExecutor(max_workers=4)
atexit.register(lambda: _ASYNC_BRIDGE_EXECUTOR.shutdown(wait=False))


def _run_async(coroutine: Any) -> Any:
    """Execute a coroutine from sync node code in a loop-safe way."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    # If an event loop is already active in this thread (for example under ASGI),
    # execute the coroutine on a separate thread with its own loop.
    future = _ASYNC_BRIDGE_EXECUTOR.submit(asyncio.run, coroutine)
    return future.result()


NODE_ARTIFACT_MAP: dict[WorkflowNode, ArtifactType] = {
    WorkflowNode.BRIEFING_INTAKE: ArtifactType.SELECTION_BRIEFING,
    WorkflowNode.BRIEFING_AUTHOR: ArtifactType.PROPOSITION_SHEET,
    WorkflowNode.BRIEFING_VALIDATION: ArtifactType.TREATMENT_SHEET,
    WorkflowNode.AUDIENCE_DESIGN: ArtifactType.AUDIENCE_DEFINITION,
    WorkflowNode.CAMPAIGN_CONFIGURATION: ArtifactType.CAMPAIGN_CONFIGURATION,
    WorkflowNode.TEST_GENERATION: ArtifactType.CONTACT_RULES,
    WorkflowNode.TEST_EXECUTION: ArtifactType.VOLUME_CONSTRAINTS,
    WorkflowNode.SIMULATION: ArtifactType.CONTROL_GROUP_DEFINITION,
    WorkflowNode.REPORTING: ArtifactType.REPORTING_CONFIGURATION,
}


def _next_in_order(node: WorkflowNode) -> WorkflowNode | None:
    index = ORDERED_NODES.index(node)
    if index == len(ORDERED_NODES) - 1:
        return None
    return ORDERED_NODES[index + 1]


def _track_node(
    state: CampaignState,
    node: WorkflowNode,
    started_at: float,
    status: str,
    output_data: dict[str, Any] | None = None,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    langsmith_tracker.track_workflow_execution(
        workflow_id=state.workflow_id,
        campaign_id=state.campaign_id,
        event_name=f"node.{node.value}",
        status=status,
        latency_ms=(time.perf_counter() - started_at) * 1000,
        input_data={"node": node.value},
        output_data=output_data or {},
        error_message=error_message,
        metadata=metadata,
    )


def _run_node(
    raw_state: dict[str, Any],
    node: WorkflowNode,
    artifact_name: str,
    artifact_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    state = CampaignState.from_dict(raw_state)
    author = f"workflow:{state.workflow_id}"
    mapped_artifact_type = NODE_ARTIFACT_MAP.get(node)

    override = state.manual_overrides.get(node.value)
    if override and override.active:
        state.mark_node_started(node)
        if mapped_artifact_type is not None:
            artifact_service.generate_artifact(
                campaign_id=state.campaign_id,
                artifact_type=mapped_artifact_type,
                content=override.payload,
                author=author,
            )
        state.artifacts[node.value] = {
            "artifact": artifact_name,
            "source": "manual_override",
            "payload": override.payload,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_node_completed(
            node,
            {
                "applied_override": True,
                "actor": override.actor,
                "reason": override.reason,
            },
        )
        state.set_next_node(_next_in_order(node))
        _track_node(
            state,
            node,
            started_at,
            status="completed",
            output_data={
                "source": "manual_override",
                "next_node": state.next_node.value if state.next_node else None,
            },
            metadata={"manual_override": True},
        )
        return state.to_dict()

    state.mark_node_started(node)
    if mapped_artifact_type is not None:
        artifact_service.generate_artifact(
            campaign_id=state.campaign_id,
            artifact_type=mapped_artifact_type,
            content=artifact_payload or {},
            author=author,
        )
    state.artifacts[node.value] = {
        "artifact": artifact_name,
        "source": "orchestration_placeholder",
        "payload": artifact_payload or {},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    state.mark_node_completed(node, {"applied_override": False})
    state.set_next_node(_next_in_order(node))
    _track_node(
        state,
        node,
        started_at,
        status="completed",
        output_data={
            "source": "orchestration_placeholder",
            "next_node": state.next_node.value if state.next_node else None,
        },
        metadata={"manual_override": False},
    )
    return state.to_dict()


def briefing_intake_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    return _run_node(raw_state, WorkflowNode.BRIEFING_INTAKE, "briefing_intake_result")


def briefing_author_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"status": "authored", "notes": "Template-generated briefing draft."}
    return _run_node(raw_state, WorkflowNode.BRIEFING_AUTHOR, "briefing_author_result", payload)


def briefing_validation_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"status": "valid", "validation_rules": ["required_fields_present"]}
    return _run_node(raw_state, WorkflowNode.BRIEFING_VALIDATION, "briefing_validation_result", payload)


def audience_design_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"segments": ["default_segment"], "strategy": "deterministic_placeholder"}
    return _run_node(raw_state, WorkflowNode.AUDIENCE_DESIGN, "audience_design_result", payload)


def campaign_configuration_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"channel": "email", "frequency_cap": 1}
    return _run_node(
        raw_state,
        WorkflowNode.CAMPAIGN_CONFIGURATION,
        "campaign_configuration_result",
        payload,
    )


def test_generation_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"tests": ["smoke_test", "business_rule_test"]}
    return _run_node(raw_state, WorkflowNode.TEST_GENERATION, "test_generation_result", payload)


def test_execution_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"executed": True, "pass_rate": 1.0}
    return _run_node(raw_state, WorkflowNode.TEST_EXECUTION, "test_execution_result", payload)


def testing_platform_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    """Execute the full Phase 7 automated testing platform."""
    started_at = time.perf_counter()
    state = CampaignState.from_dict(raw_state)
    node = WorkflowNode.TESTING_PLATFORM
    state.mark_node_started(node)

    campaign_design = {
        "channels": ["email"],
        "budget": 0,
        "audience_size": 0,
        "known_failures": [],
    }
    config_artifact = state.artifacts.get(WorkflowNode.CAMPAIGN_CONFIGURATION.value, {})
    if isinstance(config_artifact.get("payload"), dict):
        campaign_design.update(config_artifact["payload"])

    framework = AutomatedTestExecutionFramework()
    framework_output = _run_async(
        framework.execute(
            AgentInput(
                workflow_id=state.workflow_id,
                campaign_id=str(state.campaign_id),
                context={"campaign_design": campaign_design},
            )
        )
    )

    if framework_output.status != "success":
        state.status = WorkflowRunStatus.FAILED
        state.last_error = framework_output.message
        state.artifacts[node.value] = {
            "artifact": "testing_platform_result",
            "status": "failed",
            "errors": framework_output.errors,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_node_completed(node, {"status": "failed"})
        state.set_next_node(None)
        _track_node(
            state,
            node,
            started_at,
            status="failed",
            output_data={"status": "failed"},
            error_message=framework_output.message,
        )
        return state.to_dict()

    execution_data = framework_output.data.get("execution", {})
    report_data = framework_output.data.get("report", {})
    audit_data = framework_output.data.get("audit_trail", [])
    state.artifacts[node.value] = {
        "artifact": "testing_platform_result",
        "status": "success",
        "execution_summary": execution_data.get("summary", {}),
        "report_summary": report_data.get("summary", {}),
        "audit_event_count": len(audit_data),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    state.mark_node_completed(
        node,
        {
            "status": "success",
            "executed_tests": execution_data.get("summary", {}).get("total", 0),
            "pass_rate": execution_data.get("summary", {}).get("pass_rate", 0.0),
        },
    )
    state.set_next_node(_next_in_order(node))
    _track_node(
        state,
        node,
        started_at,
        status="completed",
        output_data={
            "status": "success",
            "executed_tests": execution_data.get("summary", {}).get("total", 0),
            "pass_rate": execution_data.get("summary", {}).get("pass_rate", 0.0),
        },
    )
    return state.to_dict()


def simulation_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"simulation_runs": 1, "risk_score": 0.0}
    return _run_node(raw_state, WorkflowNode.SIMULATION, "simulation_result", payload)


def ab_testing_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"variants": ["A", "B"], "winner": "A"}
    return _run_node(raw_state, WorkflowNode.AB_TESTING, "ab_testing_result", payload)


def business_approval_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    started_at = time.perf_counter()
    state = CampaignState.from_dict(raw_state)
    node = WorkflowNode.BUSINESS_APPROVAL

    state.mark_node_started(node)

    approval = state.approvals.get(node.value)
    if approval is None or approval.decision == ApprovalDecision.PENDING:
        state.awaiting_approval = True
        state.pending_approval_for = node
        state.status = WorkflowRunStatus.WAITING_APPROVAL
        submitted = artifact_service.submit_all_for_approval(state.campaign_id)
        state.artifacts[node.value] = {
            "artifact": "business_approval_result",
            "status": "pending",
            "submitted_artifacts": [item.artifact_type.value for item in submitted],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_node_completed(node, {"approval": "pending"})
        state.set_next_node(node)
        _track_node(
            state,
            node,
            started_at,
            status="waiting_approval",
            output_data={"approval": "pending"},
            metadata={"approval_state": "pending"},
        )
        return state.to_dict()

    if approval.decision == ApprovalDecision.REJECTED:
        artifact_service.review_all_pending(
            campaign_id=state.campaign_id,
            reviewer=approval.approver,
            approve=False,
            comment=approval.comment,
        )
        state.awaiting_approval = False
        state.pending_approval_for = None
        state.status = WorkflowRunStatus.FAILED
        state.last_error = "Business approval rejected."
        state.artifacts[node.value] = {
            "artifact": "business_approval_result",
            "status": "rejected",
            "comment": approval.comment,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_node_completed(node, {"approval": "rejected"})
        state.set_next_node(None)
        _track_node(
            state,
            node,
            started_at,
            status="failed",
            output_data={"approval": "rejected"},
            error_message=state.last_error,
            metadata={"approval_state": "rejected"},
        )
        return state.to_dict()

    artifact_service.review_all_pending(
        campaign_id=state.campaign_id,
        reviewer=approval.approver,
        approve=True,
        comment=approval.comment,
    )
    state.awaiting_approval = False
    state.pending_approval_for = None
    state.artifacts[node.value] = {
        "artifact": "business_approval_result",
        "status": "approved",
        "comment": approval.comment,
        "approver": approval.approver,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    state.mark_node_completed(node, {"approval": "approved"})
    state.set_next_node(WorkflowNode.DEPLOYMENT)
    _track_node(
        state,
        node,
        started_at,
        status="completed",
        output_data={"approval": "approved", "next_node": WorkflowNode.DEPLOYMENT.value},
        metadata={"approval_state": "approved"},
    )
    return state.to_dict()


def deployment_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    payload = {"deployment_status": "scheduled"}
    return _run_node(raw_state, WorkflowNode.DEPLOYMENT, "deployment_result", payload)


def reporting_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    started_at = time.perf_counter()
    state = CampaignState.from_dict(raw_state)
    node = WorkflowNode.REPORTING
    state.mark_node_started(node)
    state.artifacts[node.value] = {
        "artifact": "reporting_result",
        "summary": "Campaign orchestration completed.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    state.mark_node_completed(node, {"completed": True})
    state.status = WorkflowRunStatus.COMPLETED
    state.set_next_node(None)
    _track_node(
        state,
        node,
        started_at,
        status="completed",
        output_data={"status": "completed"},
    )
    return state.to_dict()


def control_router_node(raw_state: dict[str, Any]) -> dict[str, Any]:
    """No-op node used as a central control decision point."""
    state = CampaignState.from_dict(raw_state)
    state.mark_event("control.router", {"status": state.status.value})
    langsmith_tracker.track_workflow_execution(
        workflow_id=state.workflow_id,
        campaign_id=state.campaign_id,
        event_name="node.control_router",
        status=state.status.value,
        latency_ms=0,
        input_data={"status": state.status.value},
        output_data={"next_node": state.next_node.value if state.next_node else None},
    )
    return state.to_dict()
