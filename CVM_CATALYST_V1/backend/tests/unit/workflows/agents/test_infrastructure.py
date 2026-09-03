"""Tests for agent infrastructure components."""
import pytest
import asyncio
from src.workflows.agents.base import AgentInput, AgentOutput, BaseAgent
from src.workflows.agents.execution import ExecutionStatus


class TestAgentRegistry:
    """Tests for AgentRegistry."""
    
    def test_register_agent(self, agent_registry):
        """Test registering an agent."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent = MockAgent("test", "test_role")
        agent_registry.register("test_agent", agent)
        
        retrieved = agent_registry.get("test_agent")
        assert retrieved is not None
        assert retrieved.name == "test"
    
    def test_duplicate_registration_raises_error(self, agent_registry):
        """Test that registering duplicate agent raises error."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent = MockAgent("test", "test_role")
        agent_registry.register("test_agent", agent)
        
        with pytest.raises(ValueError):
            agent_registry.register("test_agent", agent)
    
    def test_get_by_name(self, agent_registry):
        """Test retrieving agent by name."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent = MockAgent("test_name", "test_role")
        agent_registry.register("test_agent", agent)
        
        retrieved = agent_registry.get_by_name("test_name")
        assert retrieved is not None
        assert retrieved.name == "test_name"
    
    def test_get_all_agents(self, agent_registry):
        """Test retrieving all agents."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent1 = MockAgent("agent1", "role1")
        agent2 = MockAgent("agent2", "role2")
        
        agent_registry.register("agent_1", agent1)
        agent_registry.register("agent_2", agent2)
        
        all_agents = agent_registry.get_all()
        assert len(all_agents) == 2
    
    def test_list_agents(self, agent_registry):
        """Test listing agent IDs."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent = MockAgent("test", "role")
        agent_registry.register("test_agent", agent)
        
        agents = agent_registry.list_agents()
        assert "test_agent" in agents


class TestAgentMemoryManager:
    """Tests for AgentMemoryManager."""
    
    def test_save_and_get_short_term(self, memory_manager):
        """Test saving and retrieving short-term memory."""
        memory_manager.save_short_term("key1", {"data": "value1"})
        
        retrieved = memory_manager.get_short_term("key1")
        assert retrieved is not None
        assert retrieved["data"] == "value1"
    
    def test_save_and_get_long_term(self, memory_manager):
        """Test saving and retrieving long-term memory."""
        memory_manager.save_long_term("key1", {"data": "value1"}, ttl_seconds=3600)
        
        retrieved = memory_manager.get_long_term("key1")
        assert retrieved is not None
        assert retrieved["data"] == "value1"
    
    def test_workflow_context(self, memory_manager, sample_workflow_id):
        """Test workflow context management."""
        context = {"step": "briefing_intake", "status": "pending"}
        memory_manager.set_workflow_context(sample_workflow_id, context)
        
        retrieved = memory_manager.get_workflow_context(sample_workflow_id)
        assert retrieved["step"] == "briefing_intake"
    
    def test_get_by_tags(self, memory_manager):
        """Test retrieving memory by tags."""
        memory_manager.save_short_term("key1", "value1", tags=["campaign", "briefing"])
        memory_manager.save_short_term("key2", "value2", tags=["campaign", "audience"])
        
        results = memory_manager.get_by_tags(["campaign"])
        assert len(results) == 2
    
    def test_memory_stats(self, memory_manager):
        """Test getting memory statistics."""
        memory_manager.save_short_term("key1", "value1")
        memory_manager.save_long_term("key2", "value2")
        
        stats = memory_manager.get_memory_stats()
        assert stats["short_term_entries"] == 1
        assert stats["long_term_entries"] == 1


class TestAgentObservability:
    """Tests for AgentObservability."""
    
    def test_record_metric(self, observability):
        """Test recording a metric."""
        metric_id = observability.record_metric("execution_time", 1500.5)
        assert metric_id is not None
    
    def test_record_event(self, observability):
        """Test recording an event."""
        event_id = observability.record_event("agent_executed", "Agent completed execution", severity="info")
        assert event_id is not None
    
    def test_record_alert(self, observability):
        """Test recording an alert."""
        alert_id = observability.record_alert("high_latency", "Execution took longer than expected", "high", 5000, 8500)
        assert alert_id is not None
    
    def test_performance_stats(self, observability):
        """Test retrieving performance statistics."""
        observability.record_performance("agent1", 1000)
        observability.record_performance("agent1", 1500)
        observability.record_performance("agent1", 1200)
        
        stats = observability.get_performance_stats("agent1")
        assert stats["count"] == 3
        assert stats["min_ms"] == 1000
        assert stats["max_ms"] == 1500


class TestAgentExecutionManager:
    """Tests for AgentExecutionManager."""
    
    @pytest.mark.asyncio
    async def test_execute_agent(self, execution_manager):
        """Test executing an agent."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test completed")
        
        agent = MockAgent("test", "role")
        agent_input = AgentInput(workflow_id="wf_001")
        
        record = await execution_manager.execute_agent(agent, agent_input)
        assert record.status == ExecutionStatus.COMPLETED
        assert record.execution_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_execution_history(self, execution_manager):
        """Test retrieving execution history."""
        class MockAgent(BaseAgent):
            async def execute(self, agent_input: AgentInput) -> AgentOutput:
                return AgentOutput(status="success", message="test")
        
        agent = MockAgent("test_agent", "role")
        agent_input = AgentInput(workflow_id="wf_001")
        
        await execution_manager.execute_agent(agent, agent_input)
        
        history = execution_manager.get_execution_history()
        assert len(history) >= 1