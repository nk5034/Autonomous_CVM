"""Unit tests for workflow orchestration API with Phase 7 summary exposure."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app
from src.workflows.orchestration.state import CampaignState, WorkflowNode, WorkflowRunStatus


@pytest.mark.asyncio
async def test_start_workflow_exposes_phase7_summary(monkeypatch) -> None:
    from src.api.v1.endpoints import workflow as workflow_endpoint

    class FakeOrchestrator:
        def start(self, campaign_id: int, workflow_id: str) -> CampaignState:
            state = CampaignState(
                campaign_id=campaign_id,
                workflow_id=workflow_id,
                thread_id="thread-test-001",
                status=WorkflowRunStatus.RUNNING,
                current_node=WorkflowNode.TESTING_PLATFORM,
                next_node=WorkflowNode.SIMULATION,
            )
            state.artifacts["testing_platform"] = {
                "status": "success",
                "execution_summary": {"total": 10, "passed": 9, "failed": 1, "pass_rate": 90.0},
                "report_summary": {"total_tests": 10, "passed_tests": 9, "failed_tests": 1},
                "audit_event_count": 7,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            return state

        def resume(self, workflow_id: str) -> CampaignState:
            return self.start(campaign_id=123, workflow_id=workflow_id)

        def approve(self, workflow_id: str, approver: str, decision: str, comment: str | None = None) -> CampaignState:
            state = self.start(campaign_id=123, workflow_id=workflow_id)
            state.awaiting_approval = False
            state.status = WorkflowRunStatus.COMPLETED if decision == "approved" else WorkflowRunStatus.FAILED
            state.last_error = None if decision == "approved" else "Business approval rejected."
            return state

        def get_state(self, workflow_id: str) -> CampaignState | None:
            if workflow_id == "missing":
                return None
            return self.start(campaign_id=123, workflow_id=workflow_id)

    monkeypatch.setattr(workflow_endpoint, "orchestrator", FakeOrchestrator())

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/workflows/start",
            json={"campaign_id": 123, "workflow_id": "wf_phase7_001"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["workflow_id"] == "wf_phase7_001"
        assert payload["phase7_testing_platform"]["status"] == "success"
        assert payload["phase7_testing_platform"]["execution_summary"]["total"] == 10
        assert payload["phase7_testing_platform"]["report_summary"]["passed_tests"] == 9
        assert payload["phase7_testing_platform"]["audit_event_count"] == 7


@pytest.mark.asyncio
async def test_get_workflow_state_not_found(monkeypatch) -> None:
    from src.api.v1.endpoints import workflow as workflow_endpoint

    class FakeOrchestrator:
        def start(self, campaign_id: int, workflow_id: str) -> CampaignState:
            return CampaignState(campaign_id=campaign_id, workflow_id=workflow_id, thread_id="thread")

        def resume(self, workflow_id: str) -> CampaignState:
            return self.start(campaign_id=1, workflow_id=workflow_id)

        def approve(self, workflow_id: str, approver: str, decision: str, comment: str | None = None) -> CampaignState | None:
            return None

        def get_state(self, workflow_id: str) -> CampaignState | None:
            return None

    monkeypatch.setattr(workflow_endpoint, "orchestrator", FakeOrchestrator())

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/workflows/missing")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_approve_workflow_success(monkeypatch) -> None:
    from src.api.v1.endpoints import workflow as workflow_endpoint

    class FakeOrchestrator:
        def start(self, campaign_id: int, workflow_id: str) -> CampaignState:
            return CampaignState(
                campaign_id=campaign_id,
                workflow_id=workflow_id,
                thread_id="thread-test-approve",
                status=WorkflowRunStatus.WAITING_APPROVAL,
                current_node=WorkflowNode.BUSINESS_APPROVAL,
                next_node=WorkflowNode.BUSINESS_APPROVAL,
                awaiting_approval=True,
            )

        def resume(self, workflow_id: str) -> CampaignState:
            return self.start(campaign_id=1, workflow_id=workflow_id)

        def approve(self, workflow_id: str, approver: str, decision: str, comment: str | None = None) -> CampaignState:
            if decision not in {"pending", "approved", "rejected"}:
                raise ValueError("decision must be one of: pending, approved, rejected")
            state = self.start(campaign_id=123, workflow_id=workflow_id)
            state.awaiting_approval = decision == "pending"
            if decision == "approved":
                state.status = WorkflowRunStatus.COMPLETED
                state.current_node = WorkflowNode.REPORTING
                state.next_node = None
            elif decision == "rejected":
                state.status = WorkflowRunStatus.FAILED
                state.last_error = "Business approval rejected."
            return state

        def get_state(self, workflow_id: str) -> CampaignState | None:
            return self.start(campaign_id=1, workflow_id=workflow_id)

    monkeypatch.setattr(workflow_endpoint, "orchestrator", FakeOrchestrator())

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/workflows/wf_phase7_approve/approve",
            json={"approver": "ops_user", "decision": "approved", "comment": "looks good"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["workflow_id"] == "wf_phase7_approve"
        assert payload["status"] == "completed"
        assert payload["awaiting_approval"] is False
