"""Proposition Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class PropositionAgent(BaseAgent):
    """Agent responsible for creating value propositions for each audience segment."""
    
    def __init__(self, name: str = "Proposition", role: str = "proposition"):
        super().__init__(name, role)
        self.goal = "Create value propositions for each audience segment"
        self.backstory = "Messaging strategist with deep expertise in value prop design. I craft compelling segment-specific value propositions that resonate with each audience's needs and desires."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute proposition agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract segment definitions and campaign objective
            audience_segments = agent_input.context.get("audience_segments", [])
            campaign_objective = agent_input.context.get("campaign_objective", "")
            
            # Create propositions for each segment
            propositions = self._create_propositions(audience_segments, campaign_objective)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Proposition creation completed", workflow_id=agent_input.workflow_id, count=len(propositions))
            
            return AgentOutput(
                status="success",
                message="Value propositions created successfully",
                data={
                    "propositions": propositions,
                    "proposition_count": len(propositions)
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Proposition creation failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Proposition creation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _create_propositions(self, segments: List[Dict], objective: str) -> Dict[str, Any]:
        """Create value propositions for each segment."""
        logger.info("Creating value propositions")
        
        propositions = {}
        
        proposition_templates = {
            "high_value": {
                "headline": "Premium Benefits Await You",
                "body": "Unlock exclusive privileges and premium experiences designed for our most valued customers",
                "cta": "Claim Your Premium Status",
                "tone": "exclusive, premium, aspirational"
            },
            "standard": {
                "headline": "Great Offers Just For You",
                "body": "Discover amazing deals and rewards tailored to your preferences",
                "cta": "Explore Offers",
                "tone": "friendly, approachable, value-focused"
            },
            "control": {
                "headline": "See What's New",
                "body": "Check out our latest products and services",
                "cta": "Learn More",
                "tone": "neutral, informative"
            }
        }
        
        for segment in segments:
            segment_id = segment.get("segment_id", "")
            segment_name = segment.get("name", "").lower()
            
            # Match template based on segment name
            template = None
            if "high" in segment_name and "value" in segment_name:
                template = proposition_templates["high_value"]
            elif "standard" in segment_name:
                template = proposition_templates["standard"]
            else:
                template = proposition_templates["control"]
            
            propositions[segment_id] = {
                "segment_id": segment_id,
                "segment_name": segment.get("name", ""),
                "headline": template["headline"],
                "body": template["body"],
                "cta_text": template["cta"],
                "tone": template["tone"],
                "aligned_with_objective": objective
            }
        
        return propositions