"""Shared models for the Phase 7 testing platform."""
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Supported scenario classifications."""

    FUNCTIONAL = "functional"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    REGRESSION = "regression"


class TestScenario(BaseModel):
    """Normalized test scenario model."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    scenario_type: ScenarioType = Field(..., description="Scenario category")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario details")
    expected_behavior: str = Field(..., description="Expected behavior")
    priority: str = Field(default="medium", description="Business priority")
    tags: List[str] = Field(default_factory=list)


class GeneratedTestCase(BaseModel):
    """Generated test case ready for automated execution."""

    test_case_id: str = Field(..., description="Unique test case identifier")
    scenario_id: str = Field(..., description="Related scenario identifier")
    test_type: ScenarioType = Field(..., description="Type of test")
    title: str = Field(..., description="Test case title")
    steps: List[str] = Field(default_factory=list, description="Execution steps")
    expected_result: str = Field(..., description="Expected outcome")
    severity: str = Field(default="medium", description="Business severity")
    automated: bool = Field(default=True, description="Whether automation-ready")


class TestExecutionResult(BaseModel):
    """Result of a single automated test execution."""

    test_case_id: str = Field(..., description="Executed test case ID")
    status: str = Field(..., description="Execution status")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    observed_result: str = Field(..., description="Observed result")
    error_message: Optional[str] = Field(None, description="Failure details")


class AuditTrailEntry(BaseModel):
    """Immutable audit event for compliance and traceability."""

    event_id: str = Field(..., description="Unique audit event ID")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    action: str = Field(..., description="Action name")
    actor: str = Field(..., description="Actor that performed the action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action payload")
    correlation_id: Optional[str] = Field(None, description="Workflow correlation ID")
    checksum: str = Field(..., description="Hash linking the audit chain")


class ExecutionSummary(BaseModel):
    """Aggregated execution results for one run."""

    run_id: str = Field(..., description="Unique run identifier")
    total_tests: int = Field(..., description="Total tests executed")
    passed_tests: int = Field(..., description="Tests passed")
    failed_tests: int = Field(..., description="Tests failed")
    pass_rate: float = Field(..., description="Pass rate percentage")
    started_at: str = Field(..., description="Start timestamp")
    completed_at: str = Field(..., description="Completion timestamp")
