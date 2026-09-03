"""Agent framework and all agents for workflow orchestration."""

# Infrastructure
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.registry import AgentRegistry
from src.workflows.agents.factory import AgentFactory
from src.workflows.agents.execution import AgentExecutionManager, ExecutionStatus, ExecutionRecord
from src.workflows.agents.memory import AgentMemoryManager, MemoryEntry
from src.workflows.agents.observability import AgentObservability, Metric, MetricType, Event, Alert

# Tools
from src.workflows.agents.tools import (
    BriefingTool,
    AudienceTool,
    QueryTool,
    TestTool,
    DeploymentTool,
    ReportingTool,
    get_all_tools,
)

# Campaign Planning Agents
from src.workflows.agents.campaign_planning import (
    BriefingIntakeAgent,
    BriefingAuthorAgent,
    BriefingValidatorAgent,
    AudienceDesignerAgent,
)

# Query & Targeting Agents
from src.workflows.agents.query_targeting import (
    QueryBuilderAgent,
    PropositionAgent,
    TreatmentAgent,
    MetadataAgent,
)

# Testing Agents
from src.workflows.agents.testing import (
    TestScenarioAgent,
    TestCaseAgent,
    SyntheticDataAgent,
    SimulationAgent,
    TestScenarioExtractorAgent,
    FunctionalTestGeneratorAgent,
    NegativeTestGeneratorAgent,
    BoundaryTestGeneratorAgent,
    RegressionTestGeneratorAgent,
    TestRunnerAgent,
    AutomatedTestExecutionFramework,
    TestExecutionReporter,
    AuditTrailManager,
)

# Deployment Agents
from src.workflows.agents.deployment import (
    ABTestingAgent,
    ApprovalAgent,
    DeploymentAgent,
    ReportingAgent,
)

__all__ = [
    # Infrastructure
    "BaseAgent",
    "AgentInput",
    "AgentOutput",
    "AgentRegistry",
    "AgentFactory",
    "AgentExecutionManager",
    "ExecutionStatus",
    "ExecutionRecord",
    "AgentMemoryManager",
    "MemoryEntry",
    "AgentObservability",
    "Metric",
    "MetricType",
    "Event",
    "Alert",
    # Tools
    "BriefingTool",
    "AudienceTool",
    "QueryTool",
    "TestTool",
    "DeploymentTool",
    "ReportingTool",
    "get_all_tools",
    # Campaign Planning Agents
    "BriefingIntakeAgent",
    "BriefingAuthorAgent",
    "BriefingValidatorAgent",
    "AudienceDesignerAgent",
    # Query & Targeting Agents
    "QueryBuilderAgent",
    "PropositionAgent",
    "TreatmentAgent",
    "MetadataAgent",
    # Testing Agents
    "TestScenarioAgent",
    "TestCaseAgent",
    "SyntheticDataAgent",
    "SimulationAgent",
    "TestScenarioExtractorAgent",
    "FunctionalTestGeneratorAgent",
    "NegativeTestGeneratorAgent",
    "BoundaryTestGeneratorAgent",
    "RegressionTestGeneratorAgent",
    "TestRunnerAgent",
    "AutomatedTestExecutionFramework",
    "TestExecutionReporter",
    "AuditTrailManager",
    # Deployment Agents
    "ABTestingAgent",
    "ApprovalAgent",
    "DeploymentAgent",
    "ReportingAgent",
]