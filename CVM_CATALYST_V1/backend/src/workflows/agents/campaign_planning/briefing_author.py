"""Briefing Author Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class BriefingAuthorAgent(BaseAgent):
    """Agent responsible for enriching and refining campaign briefing with strategic context."""
    
    def __init__(self, name: str = "BriefingAuthor", role: str = "briefing_author"):
        super().__init__(name, role)
        self.goal = "Enrich and refine campaign briefing with strategic context"
        self.backstory = "Campaign strategist with expertise in marketing fundamentals. I enrich briefs with strategic insights, best practices, and measurable success criteria."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute briefing author agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract normalized briefing from context
            normalized_briefing = agent_input.context.get("normalized_briefing", {})
            
            # Enrich briefing
            enriched = self._enrich_briefing(normalized_briefing)
            
            # Define success criteria
            success_criteria = self._define_success_criteria(normalized_briefing)
            
            # Define channel strategy
            channel_strategy = self._define_channel_strategy(normalized_briefing)
            
            # Assess risks
            risk_assessment = self._assess_risks(normalized_briefing)
            
            # Define timeline
            timeline = self._define_timeline(normalized_briefing)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(enriched)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Briefing authorship completed", workflow_id=agent_input.workflow_id)
            
            return AgentOutput(
                status="success",
                message="Briefing enrichment completed successfully",
                data={
                    "enriched_briefing": enriched,
                    "success_criteria": success_criteria,
                    "channel_strategy": channel_strategy,
                    "risk_assessment": risk_assessment,
                    "timeline": timeline,
                    "recommendations": recommendations
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Briefing authorship failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Briefing authorship failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _enrich_briefing(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich briefing with strategic elements."""
        logger.info("Enriching briefing")
        
        enriched = briefing.copy()
        enriched["strategic_insights"] = [
            "Focus on value proposition differentiation",
            "Emphasize customer pain points in messaging",
            "Leverage data-driven targeting for precision"
        ]
        enriched["best_practices"] = [
            "A/B test all creative variations",
            "Monitor engagement metrics in real-time",
            "Maintain consistent brand voice across channels"
        ]
        
        return enriched
    
    def _define_success_criteria(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Define measurable success criteria."""
        logger.info("Defining success criteria")
        
        return {
            "primary_metric": "conversion_rate",
            "target_conversion_rate": 0.02,
            "secondary_metrics": ["open_rate", "click_rate", "roi"],
            "kpis": briefing.get("kpis", []),
            "success_threshold": 0.80
        }
    
    def _define_channel_strategy(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Define strategy for each channel."""
        logger.info("Defining channel strategy")
        
        channels = briefing.get("channels", [])
        strategy = {}
        
        for channel in channels:
            if channel.lower() == "email":
                strategy[channel] = {
                    "frequency": "weekly",
                    "optimal_send_time": "Tuesday 10:00 AM",
                    "personalization": True
                }
            elif channel.lower() == "sms":
                strategy[channel] = {
                    "frequency": "bi-weekly",
                    "optimal_send_time": "Wednesday 2:00 PM",
                    "character_limit": 160
                }
            elif channel.lower() == "push":
                strategy[channel] = {
                    "frequency": "daily",
                    "optimal_send_time": "Morning 9:00 AM",
                    "personalization": True
                }
            else:
                strategy[channel] = {
                    "frequency": "custom",
                    "optimal_send_time": "TBD",
                    "personalization": True
                }
        
        return strategy
    
    def _assess_risks(self, briefing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess potential risks."""
        logger.info("Assessing risks")
        
        risks = []
        
        if briefing.get("budget", 0) > 500000:
            risks.append({
                "risk_type": "high_budget",
                "description": "Large budget allocation increases execution risk",
                "mitigation": "Implement phased rollout and continuous monitoring"
            })
        
        if len(briefing.get("channels", [])) > 3:
            risks.append({
                "risk_type": "channel_complexity",
                "description": "Multiple channels increase coordination complexity",
                "mitigation": "Assign dedicated channel managers"
            })
        
        return risks
    
    def _define_timeline(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Define campaign timeline."""
        logger.info("Defining timeline")
        
        return {
            "phase_1_planning": "Days 1-3",
            "phase_2_targeting": "Days 4-7",
            "phase_3_testing": "Days 8-14",
            "phase_4_deployment": "Days 15-21",
            "monitoring_period": "Days 22-35",
            "reporting": "Day 36"
        }
    
    def _generate_recommendations(self, enriched: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations."""
        logger.info("Generating recommendations")
        
        return [
            "Conduct audience research to validate targeting assumptions",
            "Develop creative variations for A/B testing",
            "Establish baseline metrics for performance comparison",
            "Create contingency plans for high-risk scenarios",
            "Schedule stakeholder check-ins at key milestones"
        ]