"""Unit tests for orchestration to artifact generation integration."""
from types import SimpleNamespace

from src.workflows.agents.base import AgentOutput
from src.workflows.orchestration import nodes
from src.workflows.orchestration.state import CampaignState, WorkflowNode


def test_briefing_author_generates_artifact(monkeypatch) -> None:
    captured: dict[str, str] = {}

    class FakeArtifactService:
        def generate_artifact(self, campaign_id, artifact_type, content, author):  # noqa: ANN001
            captured["campaign_id"] = str(campaign_id)
            captured["artifact_type"] = artifact_type.value
            captured["author"] = author
            return SimpleNamespace(artifact_type=artifact_type)

    monkeypatch.setattr(nodes, "artifact_service", FakeArtifactService())

    state = CampaignState(
        campaign_id=901,
        workflow_id="wf-901",
        thread_id="th-901",
        next_node=WorkflowNode.BRIEFING_AUTHOR,
    )

    result = nodes.briefing_author_node(state.to_dict())
    new_state = CampaignState.from_dict(result)

    assert captured["campaign_id"] == "901"
    assert captured["artifact_type"] == "proposition_sheet"
    assert captured["author"] == "workflow:wf-901"
    assert new_state.next_node == WorkflowNode.BRIEFING_VALIDATION


def test_business_approval_submits_artifacts(monkeypatch) -> None:
    captured: dict[str, int] = {"submitted": 0}

    class FakeArtifactService:
        def submit_all_for_approval(self, campaign_id):  # noqa: ANN001
            captured["submitted"] += 1
            return [SimpleNamespace(artifact_type=SimpleNamespace(value="selection_briefing"))]

        def review_all_pending(self, campaign_id, reviewer, approve, comment):  # noqa: ANN001
            return []

    monkeypatch.setattr(nodes, "artifact_service", FakeArtifactService())

    state = CampaignState(
        campaign_id=902,
        workflow_id="wf-902",
        thread_id="th-902",
        next_node=WorkflowNode.BUSINESS_APPROVAL,
    )

    result = nodes.business_approval_node(state.to_dict())
    new_state = CampaignState.from_dict(result)

    assert captured["submitted"] == 1
    assert new_state.awaiting_approval is True
    assert new_state.pending_approval_for == WorkflowNode.BUSINESS_APPROVAL


def test_testing_platform_node_runs_framework(monkeypatch) -> None:
    class FakeFramework:
        async def execute(self, agent_input):  # noqa: ANN001
            return AgentOutput(
                status="success",
                message="ok",
                data={
                    "execution": {"summary": {"total": 5, "pass_rate": 80.0}},
                    "report": {"summary": {"total_tests": 5, "passed_tests": 4}},
                    "audit_trail": [{"event_id": "audit_000001"}],
                },
            )

    monkeypatch.setattr(nodes, "AutomatedTestExecutionFramework", FakeFramework)

    state = CampaignState(
        campaign_id=903,
        workflow_id="wf-903",
        thread_id="th-903",
        next_node=WorkflowNode.TESTING_PLATFORM,
    )

    result = nodes.testing_platform_node(state.to_dict())
    new_state = CampaignState.from_dict(result)

    artifact = new_state.artifacts[WorkflowNode.TESTING_PLATFORM.value]
    assert artifact["status"] == "success"
    assert artifact["execution_summary"]["total"] == 5
    assert artifact["report_summary"]["total_tests"] == 5
    assert artifact["audit_event_count"] == 1
    assert new_state.next_node == WorkflowNode.SIMULATION
