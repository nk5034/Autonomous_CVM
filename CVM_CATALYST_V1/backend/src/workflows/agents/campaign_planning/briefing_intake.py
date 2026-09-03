"""Briefing Intake Agent for campaign workflow."""
from typing import Dict, Any, Optional
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class BriefingIntakeAgent(BaseAgent):
    """Agent responsible for receiving and normalizing campaign briefing data."""
    
    def __init__(self, name: str = "BriefingIntake", role: str = "briefing_intake"):
        super().__init__(name, role)
        self.goal = "Receive and normalize campaign briefing data"
        self.backstory = "Entry point for campaign briefs. I normalize format, validate required fields, and prepare briefs for strategic enrichment."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute briefing intake agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract briefing content from context
            briefing_content = agent_input.context.get("briefing_content", {})
            
            # Normalize briefing
            normalized = self._normalize_briefing(briefing_content)
            
            # Validate briefing
            validation_result = self._validate_briefing(normalized)
            
            # Generate briefing ID
            briefing_id = f"brief_{agent_input.workflow_id}_{int(datetime.now(UTC).timestamp())}"
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Briefing intake completed", briefing_id=briefing_id, workflow_id=agent_input.workflow_id)
            
            return AgentOutput(
                status="success",
                message="Briefing intake completed successfully",
                data={
                    "briefing_id": briefing_id,
                    "normalized_briefing": normalized,
                    "validation_result": validation_result,
                    "ready_for_enrichment": validation_result.get("is_valid", False)
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Briefing intake failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Briefing intake failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _normalize_briefing(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize briefing content."""
        logger.info("Normalizing briefing")
        
        normalized = {
            "objective": briefing.get("objective", "").strip(),
            "target_audience": briefing.get("target_audience", "").strip(),
            "channels": briefing.get("channels", []),
            "budget": float(briefing.get("budget", 0)),
            "duration": briefing.get("duration", "").strip(),
            "start_date": briefing.get("start_date", ""),
            "end_date": briefing.get("end_date", ""),
            "kpis": briefing.get("kpis", []),
            "constraints": briefing.get("constraints", []),
            "additional_notes": briefing.get("additional_notes", "").strip(),
            "created_at": datetime.now(UTC).isoformat()
        }
        
        logger.info("Briefing normalized", objective=normalized["objective"])
        return normalized
    
    def _validate_briefing(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Validate briefing using tool."""
        logger.info("Validating briefing structure")
        return briefing_tool.validate_briefing(briefing)