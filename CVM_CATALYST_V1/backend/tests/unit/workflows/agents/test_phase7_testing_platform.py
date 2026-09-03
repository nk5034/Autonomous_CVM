"""Unit tests for Phase 7 testing platform components."""
import pytest

from src.workflows.agents.base import AgentInput, AgentOutput
from src.workflows.agents.testing import (
    AutomatedTestExecutionFramework,
    BoundaryTestGeneratorAgent,
    FunctionalTestGeneratorAgent,
    NegativeTestGeneratorAgent,
    RegressionTestGeneratorAgent,
    TestRunnerAgent,
    TestScenarioExtractorAgent,
)


@pytest.mark.asyncio
async def test_scenario_extractor_produces_all_categories(sample_workflow_id):
    """Scenario extractor should produce functional/negative/boundary/regression scenarios."""
    agent = TestScenarioExtractorAgent()
    agent_input = AgentInput(
        workflow_id=sample_workflow_id,
        context={
            "campaign_design": {
                "channels": ["email", "sms"],
                "budget": 50000,
                "audience_size": 100000,
                "known_failures": ["duplicate audience joins"],
            }
        },
    )

    output = await agent.execute(agent_input)

    assert output.status == "success"
    assert output.data["scenario_count"] >= 5

    scenario_types = {item["scenario_type"] for item in output.data["extracted_scenarios"]}
    assert {"functional", "negative", "boundary", "regression"}.issubset(scenario_types)


@pytest.mark.asyncio
async def test_generators_build_test_cases(sample_workflow_id):
    """All generators should convert scenarios into category-specific test cases."""
    extractor = TestScenarioExtractorAgent()
    extracted = await extractor.execute(
        AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "campaign_design": {
                    "channels": ["email"],
                    "known_failures": ["metadata mismatch"],
                }
            },
        )
    )

    context = {"extracted_scenarios": extracted.data["extracted_scenarios"]}

    functional = await FunctionalTestGeneratorAgent().execute(
        AgentInput(workflow_id=sample_workflow_id, context=context)
    )
    negative = await NegativeTestGeneratorAgent().execute(
        AgentInput(workflow_id=sample_workflow_id, context=context)
    )
    boundary = await BoundaryTestGeneratorAgent().execute(
        AgentInput(workflow_id=sample_workflow_id, context=context)
    )
    regression = await RegressionTestGeneratorAgent().execute(
        AgentInput(workflow_id=sample_workflow_id, context=context)
    )

    assert functional.status == "success"
    assert negative.status == "success"
    assert boundary.status == "success"
    assert regression.status == "success"

    assert functional.data["functional_case_count"] >= 1
    assert negative.data["negative_case_count"] >= 1
    assert boundary.data["boundary_case_count"] >= 1
    assert regression.data["regression_case_count"] >= 1


@pytest.mark.asyncio
async def test_test_runner_executes_all_cases(sample_workflow_id):
    """Test runner should execute all supplied cases and compute summary."""
    runner = TestRunnerAgent()
    cases = [
        {
            "test_case_id": "case_001",
            "steps": ["step1", "step2"],
        },
        {
            "test_case_id": "case_002",
            "steps": ["step1"],
        },
    ]

    output = await runner.execute(
        AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "all_test_cases": cases,
                "execution_overrides": {"case_002": "failed"},
            },
        )
    )

    assert output.status == "success"
    assert output.data["summary"]["total"] == 2
    assert output.data["summary"]["failed"] == 1


@pytest.mark.asyncio
async def test_automated_execution_framework_end_to_end(sample_workflow_id):
    """Full framework should generate cases, execute them, report, and emit audit trail."""
    framework = AutomatedTestExecutionFramework()

    output = await framework.execute(
        AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "campaign_design": {
                    "channels": ["email", "push"],
                    "budget": 70000,
                    "audience_size": 120000,
                    "known_failures": ["null channel export"],
                }
            },
        )
    )

    assert output.status == "success"
    assert "execution" in output.data
    assert "report" in output.data
    assert len(output.data["audit_trail"]) >= 4
    assert output.data["report"]["summary"]["total_tests"] >= 1


@pytest.mark.asyncio
async def test_automated_execution_framework_fails_fast_on_generation_error(sample_workflow_id):
    """Framework should stop and return failure if any generator stage fails."""
    framework = AutomatedTestExecutionFramework()

    class FailingGenerator:
        async def execute(self, agent_input):  # noqa: ANN001
            return AgentOutput(
                status="failed",
                message="generation exploded",
                errors=["synthetic failure"],
                data={},
            )

    framework.negative_generator = FailingGenerator()

    output = await framework.execute(
        AgentInput(
            workflow_id=sample_workflow_id,
            context={"campaign_design": {"channels": ["email"]}},
        )
    )

    assert output.status == "failed"
    assert output.data["failed_stage"] == "negative"
    assert "synthetic failure" in output.errors
