"""Tests for query targeting, testing, and deployment agents."""
import pytest
from src.workflows.agents.base import AgentInput
from src.workflows.agents.query_targeting import (
    QueryBuilderAgent,
    PropositionAgent,
    TreatmentAgent,
    MetadataAgent,
)
from src.workflows.agents.testing import (
    TestScenarioAgent,
    TestCaseAgent,
    SyntheticDataAgent,
    SimulationAgent,
)
from src.workflows.agents.deployment import (
    ABTestingAgent,
    ApprovalAgent,
    DeploymentAgent,
    ReportingAgent,
)


class TestQueryTargetingAgents:
    """Tests for query targeting agents."""
    
    @pytest.mark.asyncio
    async def test_query_builder_agent(self, sample_workflow_id):
        """Test QueryBuilderAgent execution."""
        agent = QueryBuilderAgent()
        
        segment_definitions = {
            "high_value": {"segment_name": "High Value", "criteria": {}},
            "standard": {"segment_name": "Standard", "criteria": {}}
        }
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"segment_definitions": segment_definitions}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "queries" in output.data
    
    @pytest.mark.asyncio
    async def test_proposition_agent(self, sample_workflow_id):
        """Test PropositionAgent execution."""
        agent = PropositionAgent()
        
        audience_segments = [
            {"segment_id": "high_value", "name": "High Value"},
            {"segment_id": "standard", "name": "Standard"}
        ]
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "audience_segments": audience_segments,
                "campaign_objective": "Increase engagement"
            }
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "propositions" in output.data
    
    @pytest.mark.asyncio
    async def test_treatment_agent(self, sample_workflow_id):
        """Test TreatmentAgent execution."""
        agent = TreatmentAgent()
        
        audience_segments = [
            {"segment_id": "high_value", "name": "High Value"},
            {"segment_id": "standard", "name": "Standard"}
        ]
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"audience_segments": audience_segments}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "treatments" in output.data
    
    @pytest.mark.asyncio
    async def test_metadata_agent(self, sample_workflow_id):
        """Test MetadataAgent execution."""
        agent = MetadataAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"campaign_data": {"name": "Test Campaign"}}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "metadata" in output.data


class TestTestingAgents:
    """Tests for testing phase agents."""
    
    @pytest.mark.asyncio
    async def test_test_scenario_agent(self, sample_workflow_id):
        """Test TestScenarioAgent execution."""
        agent = TestScenarioAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"campaign_design": {}}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "test_scenarios" in output.data
        assert output.data["scenario_count"] > 0
    
    @pytest.mark.asyncio
    async def test_test_case_agent(self, sample_workflow_id):
        """Test TestCaseAgent execution."""
        agent = TestCaseAgent()
        
        test_scenarios = [
            {"scenario_id": "s001", "name": "Happy Path", "expected_result": "success"}
        ]
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"test_scenarios": test_scenarios}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "test_cases" in output.data
    
    @pytest.mark.asyncio
    async def test_synthetic_data_agent(self, sample_workflow_id):
        """Test SyntheticDataAgent execution."""
        agent = SyntheticDataAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"data_requirements": {"record_count": 10000}}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "dataset_id" in output.data
        assert output.data["records_generated"] == 10000
    
    @pytest.mark.asyncio
    async def test_simulation_agent(self, sample_workflow_id):
        """Test SimulationAgent execution."""
        agent = SimulationAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "campaign_model": {},
                "test_data": {}
            }
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "simulation_id" in output.data
        assert "predicted_metrics" in output.data


class TestDeploymentAgents:
    """Tests for deployment phase agents."""
    
    @pytest.mark.asyncio
    async def test_ab_testing_agent(self, sample_workflow_id):
        """Test ABTestingAgent execution."""
        agent = ABTestingAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"campaign_design": {"total_audience": 100000}}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "test_configuration" in output.data
        assert "test_variants" in output.data
    
    @pytest.mark.asyncio
    async def test_approval_agent(self, sample_workflow_id):
        """Test ApprovalAgent execution."""
        agent = ApprovalAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={
                "campaign_summary": {"budget": 50000},
                "approvers_required": ["manager", "compliance"]
            }
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "approval_workflow_id" in output.data
        assert "required_approvals" in output.data
    
    @pytest.mark.asyncio
    async def test_deployment_agent(self, sample_campaign_id, sample_workflow_id):
        """Test DeploymentAgent execution."""
        agent = DeploymentAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            campaign_id=sample_campaign_id,
            context={
                "deployment_config": {"channels": ["email", "sms"]},
                "campaign_id": sample_campaign_id
            }
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "deployment_id" in output.data
        assert output.data["deployment_status"] == "deployed"
    
    @pytest.mark.asyncio
    async def test_reporting_agent(self, sample_campaign_id, sample_workflow_id):
        """Test ReportingAgent execution."""
        agent = ReportingAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            campaign_id=sample_campaign_id,
            context={
                "campaign_id": sample_campaign_id,
                "report_type": "summary"
            }
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "report_id" in output.data
        assert "metrics" in output.data
        assert "insights" in output.data