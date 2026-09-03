"""Workflow orchestration endpoints including Phase 7 testing-platform summary."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.core.security.rbac import require_permissions
from src.schemas.domain import (
    Phase7TestingPlatformSummary,
    WorkflowApprovalRequest,
    WorkflowRunResponse,
    WorkflowStartRequest,
)
from src.workflows.orchestration.service import CampaignWorkflowOrchestrator

router = APIRouter(prefix="/workflows", tags=["workflows"])
orchestrator = CampaignWorkflowOrchestrator()


def _to_response(state) -> WorkflowRunResponse:  # noqa: ANN001
    artifact = state.artifacts.get("testing_platform")
    phase7_summary = None

    if isinstance(artifact, dict):
        phase7_summary = Phase7TestingPlatformSummary.model_validate(
            {
                "status": artifact.get("status"),
                "execution_summary": artifact.get("execution_summary", {}),
                "report_summary": artifact.get("report_summary", {}),
                "audit_event_count": artifact.get("audit_event_count", 0),
            }
        )

    return WorkflowRunResponse(
        workflow_id=state.workflow_id,
        campaign_id=state.campaign_id,
        status=state.status.value,
        current_node=state.current_node.value if state.current_node else None,
        next_node=state.next_node.value if state.next_node else None,
        awaiting_approval=state.awaiting_approval,
        last_error=state.last_error,
        phase7_testing_platform=phase7_summary,
    )


@router.post(
    "/start",
    response_model=WorkflowRunResponse,
    summary="Start Workflow Run",
    description="Start a campaign workflow and return state, including Phase 7 testing summary when available.",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "summary": "Start workflow",
                            "value": {
                                "campaign_id": 12001,
                                "workflow_id": "wf_phase7_12001",
                            },
                        }
                    }
                }
            }
        }
    },
)
async def start_workflow(
    payload: WorkflowStartRequest,
    _: object = Depends(require_permissions(["workflow.run"])),
) -> WorkflowRunResponse:
    try:
        state = orchestrator.start(campaign_id=payload.campaign_id, workflow_id=payload.workflow_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(state)


@router.post(
    "/{workflow_id}/resume",
    response_model=WorkflowRunResponse,
    summary="Resume Workflow Run",
    description="Resume a paused or approval-waiting workflow and return latest state and Phase 7 summary.",
    responses={
        404: {
            "description": "Workflow not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Workflow state not found for workflow_id='wf_phase7_12001'."}
                }
            },
        }
    },
)
async def resume_workflow(
    workflow_id: str,
    _: object = Depends(require_permissions(["workflow.run"])),
) -> WorkflowRunResponse:
    try:
        state = orchestrator.resume(workflow_id=workflow_id)
    except ValueError as exc:
        detail = str(exc)
        status_code = 400 if "Invalid workflow_id" in detail else 404
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return _to_response(state)


@router.post(
    "/{workflow_id}/approve",
    response_model=WorkflowRunResponse,
    summary="Approve Workflow Node",
    description="Record approval decision and return latest workflow state.",
    responses={
        400: {
            "description": "Invalid approval decision",
            "content": {
                "application/json": {
                    "example": {"detail": "decision must be one of: pending, approved, rejected"}
                }
            },
        },
        404: {
            "description": "Workflow not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Workflow state not found for workflow_id='wf_phase7_12001'."}
                }
            },
        },
    },
)
async def approve_workflow(
    workflow_id: str,
    payload: WorkflowApprovalRequest,
    _: object = Depends(require_permissions(["workflow.approve"])),
) -> WorkflowRunResponse:
    try:
        state = orchestrator.approve(
            workflow_id=workflow_id,
            approver=payload.approver,
            decision=payload.decision,
            comment=payload.comment,
        )
    except ValueError as exc:
        detail = str(exc)
        if "decision must be one of" in detail or "Invalid workflow_id" in detail or "No pending approval" in detail:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if state is None:
        raise HTTPException(status_code=404, detail=f"Workflow state not found for workflow_id='{workflow_id}'.")
    return _to_response(state)


@router.get(
    "/{workflow_id}",
    response_model=WorkflowRunResponse,
    summary="Get Workflow State",
    description="Fetch latest workflow state. Response includes compact Phase 7 testing summary.",
    responses={
        200: {
            "description": "Current workflow state",
            "content": {
                "application/json": {
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
            },
        },
        404: {
            "description": "Workflow not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Workflow state not found."}
                }
            },
        },
    },
)
async def get_workflow_state(
    workflow_id: str,
    _: object = Depends(require_permissions(["workflow.read"])),
) -> WorkflowRunResponse:
    try:
        state = orchestrator.get_state(workflow_id=workflow_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if state is None:
        raise HTTPException(status_code=404, detail="Workflow state not found.")
    return _to_response(state)
