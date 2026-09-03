"""Tests for campaign planning agents."""
import pytest
from src.workflows.agents.base import AgentInput
from src.workflows.agents.campaign_planning import (
    BriefingIntakeAgent,
    BriefingAuthorAgent,
    BriefingValidatorAgent,
    AudienceDesignerAgent,
)


class TestBriefingIntakeAgent:
    """Tests for BriefingIntakeAgent."""
    
    @pytest.mark.asyncio
    async def test_valid_briefing_intake(self, sample_briefing, sample_workflow_id):
        """Test valid briefing intake."""
        agent = BriefingIntakeAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"briefing_content": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "briefing_id" in output.data
        assert "normalized_briefing" in output.data
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, sample_workflow_id):
        """Test briefing with missing required fields."""
        agent = BriefingIntakeAgent()
        
        incomplete_briefing = {"objective": "Test"}
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"briefing_content": incomplete_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert output.data["validation_result"]["is_valid"] == False
    
    @pytest.mark.asyncio
    async def test_briefing_normalization(self, sample_workflow_id):
        """Test that briefing is properly normalized."""
        agent = BriefingIntakeAgent()
        
        briefing = {
            "objective": "  Test objective  ",
            "target_audience": "Test audience",
            "channels": ["email"],
            "budget": "50000",
            "duration": "4 weeks",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "kpis": [],
            "constraints": []
        }
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"briefing_content": briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        normalized = output.data["normalized_briefing"]
        assert normalized["budget"] == 50000.0


class TestBriefingAuthorAgent:
    """Tests for BriefingAuthorAgent."""
    
    @pytest.mark.asyncio
    async def test_enrichment_adds_strategic_elements(self, sample_briefing, sample_workflow_id):
        """Test that enrichment adds strategic elements."""
        agent = BriefingAuthorAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"normalized_briefing": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "enriched_briefing" in output.data
        assert "success_criteria" in output.data
        assert "channel_strategy" in output.data
    
    @pytest.mark.asyncio
    async def test_generates_recommendations(self, sample_briefing, sample_workflow_id):
        """Test that recommendations are generated."""
        agent = BriefingAuthorAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"normalized_briefing": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "recommendations" in output.data
        assert len(output.data["recommendations"]) > 0


class TestBriefingValidatorAgent:
    """Tests for BriefingValidatorAgent."""
    
    @pytest.mark.asyncio
    async def test_validation_passes_for_valid_briefing(self, sample_briefing, sample_workflow_id):
        """Test validation passes for valid briefing."""
        agent = BriefingValidatorAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"enriched_briefing": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert output.data["is_approved"] == True
    
    @pytest.mark.asyncio
    async def test_validation_fails_for_zero_budget(self, sample_briefing, sample_workflow_id):
        """Test validation fails for zero budget."""
        agent = BriefingValidatorAgent()
        
        invalid_briefing = sample_briefing.copy()
        invalid_briefing["budget"] = 0
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"enriched_briefing": invalid_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert output.data["is_approved"] == False
        assert len(output.data["issues"]) > 0


class TestAudienceDesignerAgent:
    """Tests for AudienceDesignerAgent."""
    
    @pytest.mark.asyncio
    async def test_segment_design_creates_segments(self, sample_briefing, sample_workflow_id):
        """Test that segment design creates segments."""
        agent = AudienceDesignerAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"enriched_briefing": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "audience_segments" in output.data
        assert len(output.data["audience_segments"]) > 0
    
    @pytest.mark.asyncio
    async def test_segment_size_estimates(self, sample_briefing, sample_workflow_id):
        """Test segment size estimates are generated."""
        agent = AudienceDesignerAgent()
        
        agent_input = AgentInput(
            workflow_id=sample_workflow_id,
            context={"enriched_briefing": sample_briefing}
        )
        
        output = await agent.execute(agent_input)
        assert output.status == "success"
        assert "audience_size_estimates" in output.data
        assert "total_addressable_market" in output.data