"""Audience Designer Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import audience_tool

logger = structlog.get_logger(__name__)


class AudienceDesignerAgent(BaseAgent):
    """Agent responsible for designing and segmenting target audience for campaign."""
    
    def __init__(self, name: str = "AudienceDesigner", role: str = "audience_designer"):
        super().__init__(name, role)
        self.goal = "Design and segment target audience for campaign"
        self.backstory = "Audience strategist with deep expertise in segmentation. I design precise audience segments based on campaign objectives, business goals, and behavioral data."
        self.add_tool(audience_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute audience designer agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract validated briefing from context
            validated_briefing = agent_input.context.get("enriched_briefing", {})
            
            # Design audience segments
            segments = self._design_segments(validated_briefing)
            
            # Define segment criteria
            segment_definitions = self._define_segment_criteria(segments)
            
            # Estimate segment sizes
            audience_size_estimates = self._estimate_segment_sizes(segment_definitions)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Audience design completed", workflow_id=agent_input.workflow_id, segment_count=len(segments))
            
            return AgentOutput(
                status="success",
                message="Audience design completed successfully",
                data={
                    "audience_segments": segments,
                    "segment_definitions": segment_definitions,
                    "audience_size_estimates": audience_size_estimates,
                    "total_addressable_market": sum([est["estimated_size"] for est in audience_size_estimates.values()])
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Audience design failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Audience design failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _design_segments(self, briefing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design audience segments."""
        logger.info("Designing audience segments")
        
        campaign_objective = briefing.get("objective", "")
        
        # Use audience tool to get default segments
        segments_dict = audience_tool.segment_audience(campaign_objective)
        
        segments = []
        for segment_id, segment_data in segments_dict.items():
            segments.append({
                "segment_id": segment_id,
                "name": segment_data["name"],
                "market_share": segment_data["market_share"],
                "budget_allocation": segment_data["budget_allocation"],
                "priority": "high" if segment_data["budget_allocation"] > 0.30 else "medium" if segment_data["budget_allocation"] > 0.10 else "low"
            })
        
        return segments
    
    def _define_segment_criteria(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define detailed criteria for each segment."""
        logger.info("Defining segment criteria")
        
        definitions = {}
        
        segment_criteria = {
            "high_value": {
                "demographics": {
                    "age_range": "35-65",
                    "income_level": "75000+",
                    "education": "college_or_higher"
                },
                "behavioral": {
                    "purchase_frequency": "frequent",
                    "average_transaction_value": "high",
                    "customer_lifetime_value": "high"
                },
                "psychographic": {
                    "interests": ["premium_brands", "luxury_goods", "innovation"],
                    "values": ["quality", "exclusivity", "status"]
                }
            },
            "standard": {
                "demographics": {
                    "age_range": "25-55",
                    "income_level": "40000-75000",
                    "education": "high_school_or_college"
                },
                "behavioral": {
                    "purchase_frequency": "moderate",
                    "average_transaction_value": "medium",
                    "customer_lifetime_value": "medium"
                },
                "psychographic": {
                    "interests": ["value", "convenience", "reliability"],
                    "values": ["quality", "affordability", "trust"]
                }
            },
            "control": {
                "demographics": {
                    "age_range": "18-75",
                    "income_level": "any",
                    "education": "any"
                },
                "behavioral": {
                    "purchase_frequency": "low_to_moderate",
                    "average_transaction_value": "low_to_medium",
                    "customer_lifetime_value": "low_to_medium"
                },
                "psychographic": {
                    "interests": ["price_sensitive", "experimental"],
                    "values": ["savings", "discovery"]
                }
            }
        }
        
        for segment in segments:
            segment_id = segment["segment_id"]
            if segment_id in segment_criteria:
                definitions[segment_id] = {
                    "segment_name": segment["name"],
                    "criteria": segment_criteria[segment_id],
                    "market_share": segment["market_share"],
                    "budget_allocation": segment["budget_allocation"]
                }
        
        return definitions
    
    def _estimate_segment_sizes(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate audience size for each segment."""
        logger.info("Estimating segment sizes")
        
        total_market = 1000000  # Base market size
        estimates = {}
        
        for segment_id, definition in definitions.items():
            estimated_size = int(total_market * definition["market_share"])
            estimates[segment_id] = {
                "segment_name": definition["segment_name"],
                "estimated_size": estimated_size,
                "market_share_percentage": definition["market_share"] * 100,
                "budget_allocation_percentage": definition["budget_allocation"] * 100,
                "confidence_level": "high"
            }
        
        return estimates