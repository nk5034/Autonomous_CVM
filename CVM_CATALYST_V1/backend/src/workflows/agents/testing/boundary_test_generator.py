"""Boundary Test Generator agent for Phase 7 testing platform."""
from datetime import UTC, datetime
from typing import List

import structlog

from src.workflows.agents.base import AgentInput, AgentOutput, BaseAgent
from src.workflows.agents.testing.platform_models import GeneratedTestCase, ScenarioType, TestScenario

logger = structlog.get_logger(__name__)


class BoundaryTestGeneratorAgent(BaseAgent):
    """Generates boundary-condition automated test cases."""

    __test__ = False

    def __init__(self, name: str = "BoundaryTestGenerator", role: str = "boundary_test_generator"):
        super().__init__(name, role)

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Generate boundary test cases from extracted scenarios."""
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
                message="Boundary test cases generated",
                data={
                    "boundary_test_cases": [case.model_dump() for case in test_cases],
                    "boundary_case_count": len(test_cases),
                },
                execution_time_ms=execution_time,
            )

        except Exception as exc:
            logger.error("Boundary test generation failed", error=str(exc))
            return AgentOutput(status="failed", message=f"Boundary test generation failed: {exc}", errors=[str(exc)])

    def _build_cases(self, scenarios: List[TestScenario]) -> List[GeneratedTestCase]:
        """Transform boundary scenarios into executable test cases."""
        cases: List[GeneratedTestCase] = []
        for idx, scenario in enumerate(scenarios, start=1):
            if scenario.scenario_type != ScenarioType.BOUNDARY:
                continue

            cases.append(
                GeneratedTestCase(
                    test_case_id=f"bt_{idx:03d}",
                    scenario_id=scenario.scenario_id,
                    test_type=ScenarioType.BOUNDARY,
                    title=f"Boundary verification for {scenario.name}",
                    steps=[
                        "Prepare payload at boundary threshold",
                        "Trigger orchestration execution",
                        "Track performance and functional behavior",
                        "Assert system response remains within acceptance limits",
                    ],
                    expected_result=scenario.expected_behavior,
                    severity="high",
                )
            )

        return cases
