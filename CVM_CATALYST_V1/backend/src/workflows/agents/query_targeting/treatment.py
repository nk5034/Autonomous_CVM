"""Treatment Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class TreatmentAgent(BaseAgent):
    """Agent responsible for defining campaign treatments and creative variations."""
    
    def __init__(self, name: str = "Treatment", role: str = "treatment"):
        super().__init__(name, role)
        self.goal = "Define campaign treatments and creative variations"
        self.backstory = "Creative director with deep expertise in design and messaging. I define treatments optimized for segment preferences and channel requirements."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute treatment agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            propositions = agent_input.context.get("propositions", {})
            segments = agent_input.context.get("audience_segments", [])
            
            treatments = self._define_treatments(propositions, segments)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Treatment definition completed", workflow_id=agent_input.workflow_id)
            
            return AgentOutput(
                status="success",
                message="Treatments defined successfully",
                data={"treatments": treatments},
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Treatment definition failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Treatment definition failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _define_treatments(self, propositions: Dict, segments: List) -> Dict[str, Any]:
        """Define treatments for each segment."""
        logger.info("Defining treatments")
        
        treatments = {}
        
        for segment in segments:
            segment_id = segment.get("segment_id", "")
            segment_name = segment.get("name", "").lower()
            
            if "high" in segment_name and "value" in segment_name:
                treatment = {
                    "segment_id": segment_id,
                    "treatment_name": "Premium Rich Media",
                    "format": "rich_media",
                    "images": ["hero_image_premium.jpg"],
                    "colors": ["#FFD700", "#000000"],
                    "tone": "premium, exclusive",
                    "cta_button_color": "#FFD700"
                }
            elif "standard" in segment_name:
                treatment = {
                    "segment_id": segment_id,
                    "treatment_name": "Standard HTML",
                    "format": "html",
                    "images": ["hero_image_standard.jpg"],
                    "colors": ["#0066CC", "#FFFFFF"],
                    "tone": "friendly, approachable",
                    "cta_button_color": "#0066CC"
                }
            else:
                treatment = {
                    "segment_id": segment_id,
                    "treatment_name": "Control Text",
                    "format": "text",
                    "images": [],
                    "colors": ["#333333"],
                    "tone": "neutral, informative",
                    "cta_button_color": "#333333"
                }
            
            treatments[segment_id] = treatment
        
        return treatments