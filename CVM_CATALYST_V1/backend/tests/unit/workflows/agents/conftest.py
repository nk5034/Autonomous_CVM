"""Pytest fixtures for agent tests."""
import pytest
from src.workflows.agents.registry import AgentRegistry
from src.workflows.agents.factory import AgentFactory
from src.workflows.agents.execution import AgentExecutionManager
from src.workflows.agents.memory import AgentMemoryManager
from src.workflows.agents.observability import AgentObservability


@pytest.fixture
def agent_registry():
    """Create a clean AgentRegistry for each test."""
    registry = AgentRegistry()
    registry.clear()
    return registry


@pytest.fixture
def agent_factory():
    """Create an AgentFactory for tests."""
    return AgentFactory()


@pytest.fixture
def execution_manager():
    """Create an AgentExecutionManager for tests."""
    return AgentExecutionManager(max_concurrent=3)


@pytest.fixture
def memory_manager():
    """Create an AgentMemoryManager for tests."""
    return AgentMemoryManager()


@pytest.fixture
def observability():
    """Create an AgentObservability instance for tests."""
    return AgentObservability()


@pytest.fixture
def sample_briefing():
    """Create a sample briefing for testing."""
    return {
        "objective": "Increase customer engagement and drive conversions",
        "target_audience": "High-value customers aged 35-65 with annual income > $75,000",
        "channels": ["email", "sms", "push"],
        "budget": 50000,
        "duration": "4 weeks",
        "start_date": "2024-01-15",
        "end_date": "2024-02-15",
        "kpis": ["conversion_rate", "roi", "customer_satisfaction"],
        "constraints": ["GDPR compliant", "Mobile optimized"],
        "additional_notes": "Q1 product launch campaign"
    }


@pytest.fixture
def sample_campaign_id():
    """Provide a sample campaign ID."""
    return "camp_test_001"


@pytest.fixture
def sample_workflow_id():
    """Provide a sample workflow ID."""
    return "wf_test_001"