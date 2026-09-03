"""Reporting service for Phase 7 testing platform."""
from collections import Counter
from datetime import UTC, datetime
from typing import Dict, List

from src.workflows.agents.testing.platform_models import AuditTrailEntry, ExecutionSummary, TestExecutionResult


class TestExecutionReporter:
    """Builds execution and quality reports for generated test suites."""

    def generate_report(
        self,
        run_id: str,
        results: List[TestExecutionResult],
        audit_entries: List[AuditTrailEntry],
        started_at: str,
        completed_at: str,
    ) -> Dict[str, object]:
        """Generate an aggregate report from execution data."""
        total_tests = len(results)
        passed_tests = len([result for result in results if result.status == "passed"])
        failed_tests = len([result for result in results if result.status == "failed"])

        pass_rate = (passed_tests / total_tests * 100.0) if total_tests else 0.0

        summary = ExecutionSummary(
            run_id=run_id,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            pass_rate=round(pass_rate, 2),
            started_at=started_at,
            completed_at=completed_at,
        )

        failure_details = [
            {
                "test_case_id": result.test_case_id,
                "error_message": result.error_message,
                "observed_result": result.observed_result,
            }
            for result in results
            if result.status == "failed"
        ]

        status_distribution = Counter(result.status for result in results)
        avg_duration_ms = (
            sum(result.duration_ms for result in results) / total_tests if total_tests else 0.0
        )

        return {
            "summary": summary.model_dump(),
            "status_distribution": dict(status_distribution),
            "avg_duration_ms": round(avg_duration_ms, 2),
            "failure_details": failure_details,
            "audit": {
                "event_count": len(audit_entries),
                "last_event_timestamp": audit_entries[-1].timestamp if audit_entries else datetime.now(UTC).isoformat(),
            },
        }
