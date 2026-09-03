"""Automated execution framework for Phase 7 testing platform."""
from datetime import UTC, datetime
from typing import Any, Dict, List

from src.workflows.agents.base import AgentInput, AgentOutput
from src.workflows.agents.testing.audit_trail import AuditTrailManager
from src.workflows.agents.testing.boundary_test_generator import BoundaryTestGeneratorAgent
from src.workflows.agents.testing.functional_test_generator import FunctionalTestGeneratorAgent
from src.workflows.agents.testing.negative_test_generator import NegativeTestGeneratorAgent
from src.workflows.agents.testing.platform_models import AuditTrailEntry, TestExecutionResult
from src.workflows.agents.testing.regression_test_generator import RegressionTestGeneratorAgent
from src.workflows.agents.testing.reporting import TestExecutionReporter
from src.workflows.agents.testing.scenario_extractor import TestScenarioExtractorAgent
from src.workflows.agents.testing.test_runner import TestRunnerAgent


class AutomatedTestExecutionFramework:
    """Coordinates extraction, generation, execution, reporting, and audit."""

    def __init__(self) -> None:
        self.extractor = TestScenarioExtractorAgent()
        self.functional_generator = FunctionalTestGeneratorAgent()
        self.negative_generator = NegativeTestGeneratorAgent()
        self.boundary_generator = BoundaryTestGeneratorAgent()
        self.regression_generator = RegressionTestGeneratorAgent()
        self.runner = TestRunnerAgent()
        self.reporter = TestExecutionReporter()
        self.audit = AuditTrailManager()

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Run the full automated testing platform."""
        run_started = datetime.now(UTC).isoformat()
        self.audit.record(
            action="phase7_execution_started",
            details={"workflow_id": agent_input.workflow_id},
            actor="AutomatedTestExecutionFramework",
            correlation_id=agent_input.workflow_id,
        )

        scenario_output = await self.extractor.execute(agent_input)
        if scenario_output.status != "success":
            return scenario_output

        base_context = dict(agent_input.context)
        base_context.update(scenario_output.data)

        functional_output = await self.functional_generator.execute(
            AgentInput(
                workflow_id=agent_input.workflow_id,
                campaign_id=agent_input.campaign_id,
                user_id=agent_input.user_id,
                context=base_context,
            )
        )
        negative_output = await self.negative_generator.execute(
            AgentInput(
                workflow_id=agent_input.workflow_id,
                campaign_id=agent_input.campaign_id,
                user_id=agent_input.user_id,
                context=base_context,
            )
        )
        boundary_output = await self.boundary_generator.execute(
            AgentInput(
                workflow_id=agent_input.workflow_id,
                campaign_id=agent_input.campaign_id,
                user_id=agent_input.user_id,
                context=base_context,
            )
        )
        regression_output = await self.regression_generator.execute(
            AgentInput(
                workflow_id=agent_input.workflow_id,
                campaign_id=agent_input.campaign_id,
                user_id=agent_input.user_id,
                context=base_context,
            )
        )

        generation_outputs = [
            ("functional", functional_output),
            ("negative", negative_output),
            ("boundary", boundary_output),
            ("regression", regression_output),
        ]
        for stage_name, stage_output in generation_outputs:
            if stage_output.status != "success":
                self.audit.record(
                    action="test_generation_failed",
                    details={"stage": stage_name, "message": stage_output.message},
                    actor="AutomatedTestExecutionFramework",
                    correlation_id=agent_input.workflow_id,
                )
                return AgentOutput(
                    status="failed",
                    message=f"Test generation failed at stage: {stage_name}",
                    data={"failed_stage": stage_name},
                    errors=stage_output.errors or [stage_output.message],
                )

        all_test_cases = (
            functional_output.data.get("functional_test_cases", [])
            + negative_output.data.get("negative_test_cases", [])
            + boundary_output.data.get("boundary_test_cases", [])
            + regression_output.data.get("regression_test_cases", [])
        )

        self.audit.record(
            action="test_cases_generated",
            details={"count": len(all_test_cases)},
            actor="AutomatedTestExecutionFramework",
            correlation_id=agent_input.workflow_id,
        )

        run_output = await self.runner.execute(
            AgentInput(
                workflow_id=agent_input.workflow_id,
                campaign_id=agent_input.campaign_id,
                user_id=agent_input.user_id,
                context={
                    **base_context,
                    "all_test_cases": all_test_cases,
                },
            )
        )

        if run_output.status != "success":
            return run_output

        self.audit.record(
            action="test_run_completed",
            details=run_output.data.get("summary", {}),
            actor="AutomatedTestExecutionFramework",
            correlation_id=agent_input.workflow_id,
        )

        audit_entries = self.audit.list_entries()
        parsed_results: List[TestExecutionResult] = [
            TestExecutionResult.model_validate(item)
            for item in run_output.data.get("results", [])
        ]

        report = self.reporter.generate_report(
            run_id=run_output.data.get("run_id", "run_unknown"),
            results=parsed_results,
            audit_entries=audit_entries,
            started_at=run_output.data.get("summary", {}).get("started_at", run_started),
            completed_at=run_output.data.get("summary", {}).get("completed_at", datetime.now(UTC).isoformat()),
        )

        self.audit.record(
            action="test_report_generated",
            details={"run_id": run_output.data.get("run_id", "run_unknown")},
            actor="AutomatedTestExecutionFramework",
            correlation_id=agent_input.workflow_id,
        )

        return AgentOutput(
            status="success",
            message="Phase 7 automated testing platform executed successfully",
            data={
                "scenarios": scenario_output.data,
                "functional": functional_output.data,
                "negative": negative_output.data,
                "boundary": boundary_output.data,
                "regression": regression_output.data,
                "execution": run_output.data,
                "report": report,
                "audit_trail": [entry.model_dump() for entry in self.audit.list_entries()],
            },
        )
