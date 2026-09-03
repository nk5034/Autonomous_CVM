"""Test Runner agent for Phase 7 testing platform."""
from datetime import UTC, datetime
from typing import Any, Dict, List

import structlog

from src.workflows.agents.base import AgentInput, AgentOutput, BaseAgent
from src.workflows.agents.testing.platform_models import TestExecutionResult

logger = structlog.get_logger(__name__)


class TestRunnerAgent(BaseAgent):
    """Executes generated test cases in an automated run."""

    __test__ = False

    def __init__(self, name: str = "TestRunner", role: str = "test_runner"):
        super().__init__(name, role)

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Run test cases and return execution summary."""
        self.log_execution_start(agent_input)

        try:
            start_dt = datetime.now(UTC)

            all_cases = self._collect_cases(agent_input.context)
            overrides = agent_input.context.get("execution_overrides", {})
            results = [self._execute_case(case, overrides) for case in all_cases]

            passed = len([item for item in results if item.status == "passed"])
            failed = len(results) - passed

            execution_time = (datetime.now(UTC) - start_dt).total_seconds() * 1000
            self.log_execution_end(execution_time)

            return AgentOutput(
                status="success",
                message="Automated test run completed",
                data={
                    "run_id": f"run_{int(start_dt.timestamp())}",
                    "results": [result.model_dump() for result in results],
                    "summary": {
                        "total": len(results),
                        "passed": passed,
                        "failed": failed,
                        "pass_rate": round((passed / len(results) * 100.0), 2) if results else 0.0,
                        "started_at": start_dt.isoformat(),
                        "completed_at": datetime.now(UTC).isoformat(),
                    },
                },
                execution_time_ms=execution_time,
            )

        except Exception as exc:
            logger.error("Test run failed", error=str(exc))
            return AgentOutput(status="failed", message=f"Test run failed: {exc}", errors=[str(exc)])

    def _collect_cases(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect all generated cases across categories."""
        return list(
            context.get("all_test_cases")
            or context.get("functional_test_cases", [])
            + context.get("negative_test_cases", [])
            + context.get("boundary_test_cases", [])
            + context.get("regression_test_cases", [])
        )

    def _execute_case(self, case: Dict[str, Any], overrides: Dict[str, str]) -> TestExecutionResult:
        """Execute one case using deterministic simulation logic."""
        case_id = case.get("test_case_id", "unknown")
        forced_status = overrides.get(case_id)

        started = datetime.now(UTC)
        if forced_status in {"passed", "failed"}:
            status = forced_status
        else:
            status = "failed" if not case.get("steps") else "passed"

        duration_ms = max((datetime.now(UTC) - started).total_seconds() * 1000, 1.0)

        if status == "passed":
            return TestExecutionResult(
                test_case_id=case_id,
                status="passed",
                duration_ms=duration_ms,
                observed_result="Execution matched expected result",
                error_message=None,
            )

        return TestExecutionResult(
            test_case_id=case_id,
            status="failed",
            duration_ms=duration_ms,
            observed_result="Execution diverged from expected result",
            error_message="Deterministic test failure condition triggered",
        )
