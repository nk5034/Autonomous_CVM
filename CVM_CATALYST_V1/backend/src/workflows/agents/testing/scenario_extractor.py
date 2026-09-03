"""Test Scenario Extractor agent for Phase 7 testing platform."""
from datetime import UTC, datetime
from typing import Any, Dict, List

import structlog

from src.workflows.agents.base import AgentInput, AgentOutput, BaseAgent
from src.workflows.agents.testing.platform_models import ScenarioType, TestScenario

logger = structlog.get_logger(__name__)


class TestScenarioExtractorAgent(BaseAgent):
    """Extracts normalized scenarios from campaign design input."""

    __test__ = False

    def __init__(self, name: str = "TestScenarioExtractor", role: str = "test_scenario_extractor"):
        super().__init__(name, role)
        self.goal = "Extract and normalize test scenarios for automated execution"
        self.backstory = "QA analyst specializing in translating campaign behavior into executable scenarios."

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Extract test scenarios from context."""
        self.log_execution_start(agent_input)

        try:
            start_time = datetime.now(UTC)
            campaign_design = agent_input.context.get("campaign_design", {})
            scenarios = self._extract_scenarios(campaign_design)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)

            return AgentOutput(
                status="success",
                message="Test scenarios extracted successfully",
                data={
                    "extracted_scenarios": [scenario.model_dump() for scenario in scenarios],
                    "scenario_count": len(scenarios),
                },
                execution_time_ms=execution_time,
            )

        except Exception as exc:
            logger.error("Scenario extraction failed", error=str(exc))
            return AgentOutput(
                status="failed",
                message=f"Scenario extraction failed: {exc}",
                errors=[str(exc)],
            )

    def _extract_scenarios(self, campaign_design: Dict[str, Any]) -> List[TestScenario]:
        """Build functional, negative, boundary, and regression scenario sets."""
        channels = campaign_design.get("channels", ["email"])
        budget = float(campaign_design.get("budget", 0) or 0)
        audience_size = int(campaign_design.get("audience_size", 0) or 0)
        known_failures = campaign_design.get("known_failures", [])

        scenarios: List[TestScenario] = []

        for idx, channel in enumerate(channels, start=1):
            scenarios.append(
                TestScenario(
                    scenario_id=f"func_{idx:03d}",
                    scenario_type=ScenarioType.FUNCTIONAL,
                    name=f"Functional send via {channel}",
                    description=f"Validate successful campaign execution path for channel {channel}",
                    expected_behavior="Campaign job completes and target audience receives the message",
                    priority="high",
                    tags=["functional", channel],
                )
            )

        scenarios.append(
            TestScenario(
                scenario_id="neg_001",
                scenario_type=ScenarioType.NEGATIVE,
                name="Reject missing objective",
                description="Validate campaign creation fails when objective is empty",
                expected_behavior="Validation error returned with actionable message",
                priority="critical",
                tags=["negative", "validation"],
            )
        )

        scenarios.append(
            TestScenario(
                scenario_id="bnd_001",
                scenario_type=ScenarioType.BOUNDARY,
                name="Budget lower boundary",
                description=f"Validate behavior at budget lower limit (current={budget})",
                expected_behavior="System accepts minimum allowed budget and schedules campaign",
                priority="high",
                tags=["boundary", "budget"],
            )
        )

        scenarios.append(
            TestScenario(
                scenario_id="bnd_002",
                scenario_type=ScenarioType.BOUNDARY,
                name="Audience upper boundary",
                description=f"Validate behavior at large audience size (current={audience_size})",
                expected_behavior="System processes audience size at upper bound without timeout",
                priority="high",
                tags=["boundary", "audience"],
            )
        )

        if known_failures:
            for idx, failure in enumerate(known_failures, start=1):
                scenarios.append(
                    TestScenario(
                        scenario_id=f"reg_{idx:03d}",
                        scenario_type=ScenarioType.REGRESSION,
                        name=f"Regression guard: {failure}",
                        description=f"Confirm previously reported issue is not reintroduced: {failure}",
                        expected_behavior="Observed output matches fixed behavior and no legacy bug signal appears",
                        priority="critical",
                        tags=["regression"],
                    )
                )
        else:
            scenarios.append(
                TestScenario(
                    scenario_id="reg_001",
                    scenario_type=ScenarioType.REGRESSION,
                    name="Regression baseline suite",
                    description="Execute baseline regression suite for campaign orchestration path",
                    expected_behavior="Previously validated campaign flow remains stable",
                    priority="high",
                    tags=["regression", "baseline"],
                )
            )

        return scenarios
