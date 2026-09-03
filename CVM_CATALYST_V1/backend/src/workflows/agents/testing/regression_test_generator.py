"""Regression Test Generator agent for Phase 7 testing platform."""
from datetime import UTC, datetime
from typing import List

import structlog

from src.workflows.agents.base import AgentInput, AgentOutput, BaseAgent
from src.workflows.agents.testing.platform_models import GeneratedTestCase, ScenarioType, TestScenario

logger = structlog.get_logger(__name__)


class RegressionTestGeneratorAgent(BaseAgent):
    """Generates regression automated test cases."""

    __test__ = False

    def __init__(self, name: str = "RegressionTestGenerator", role: str = "regression_test_generator"):
        super().__init__(name, role)

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Generate regression test cases from extracted scenarios."""
        self.log_execution_start(agent_input)

        try:
            start_time = datetime.now(UTC)
            scenario_payload = agent_input.context.get("extracted_scenarios", [])
            scenarios = [TestScenario.model_validate(item) for item in scenario_payload]
            test_cases = self._build_cases(scenarios)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)

            return AgentOutput(
                status="success",
                message="Regression test cases generated",
                data={
                    "regression_test_cases": [case.model_dump() for case in test_cases],
                    "regression_case_count": len(test_cases),
                },
                execution_time_ms=execution_time,
            )

        except Exception as exc:
            logger.error("Regression test generation failed", error=str(exc))
            return AgentOutput(status="failed", message=f"Regression test generation failed: {exc}", errors=[str(exc)])

    def _build_cases(self, scenarios: List[TestScenario]) -> List[GeneratedTestCase]:
        """Transform regression scenarios into executable test cases."""
        cases: List[GeneratedTestCase] = []
        for idx, scenario in enumerate(scenarios, start=1):
            if scenario.scenario_type != ScenarioType.REGRESSION:
                continue

            cases.append(
                GeneratedTestCase(
                    test_case_id=f"rt_{idx:03d}",
                    scenario_id=scenario.scenario_id,
                    test_type=ScenarioType.REGRESSION,
                    title=f"Regression guard for {scenario.name}",
                    steps=[
                        "Load payload associated with previously fixed defect",
                        "Execute relevant workflow path",
                        "Assert previous bug signal is absent",
                        "Validate corrected business behavior remains intact",
                    ],
                    expected_result=scenario.expected_behavior,
                    severity="critical",
                )
            )

        return cases
