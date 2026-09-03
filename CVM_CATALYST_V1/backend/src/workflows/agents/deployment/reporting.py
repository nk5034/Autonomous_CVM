"""Reporting Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import reporting_tool

logger = structlog.get_logger(__name__)


class ReportingAgent(BaseAgent):
    """Agent responsible for generating comprehensive campaign reports and analytics."""
    
    def __init__(self, name: str = "Reporting", role: str = "reporting"):
        super().__init__(name, role)
        self.goal = "Generate comprehensive campaign reports and analytics"
        self.backstory = "Analytics specialist with deep expertise in campaign reporting. I generate comprehensive reports with insights, recommendations, and performance analysis."
        self.add_tool(reporting_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute reporting agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            campaign_id = agent_input.campaign_id or agent_input.context.get("campaign_id", "")
            report_type = agent_input.context.get("report_type", "summary")
            
            report = self._generate_report(campaign_id, report_type)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info(
                "Campaign report generated",
                campaign_id=campaign_id,
                report_id=report["report_id"],
                report_type=report_type
            )
            
            return AgentOutput(
                status="success",
                message="Campaign report generated successfully",
                data={
                    "report_id": report["report_id"],
                    "campaign_id": campaign_id,
                    "report_type": report_type,
                    "metrics": report["metrics"],
                    "insights": report["insights"],
                    "recommendations": report["recommendations"]
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Report generation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _generate_report(self, campaign_id: str, report_type: str) -> Dict[str, Any]:
        """Generate comprehensive campaign report."""
        logger.info("Generating campaign report", campaign_id=campaign_id, report_type=report_type)
        
        report = reporting_tool.generate_report(campaign_id, report_type)
        
        insights = self._generate_insights(report["metrics"])
        recommendations = self._generate_recommendations(report["metrics"])
        
        return {
            "report_id": report["report_id"],
            "campaign_id": campaign_id,
            "report_type": report_type,
            "metrics": report["metrics"],
            "insights": insights,
            "recommendations": recommendations,
            "generated_at": report["generated_at"]
        }
    
    def _generate_insights(self, metrics: Dict[str, float]) -> List[str]:
        """Generate insights from metrics."""
        logger.info("Generating insights from metrics")
        
        insights = []
        
        if metrics.get("open_rate", 0) > 0.25:
            insights.append("Strong email open rate indicates effective subject lines and send timing")
        
        if metrics.get("click_rate", 0) > 0.08:
            insights.append("High click-through rate shows compelling call-to-action copy")
        
        if metrics.get("conversion_rate", 0) > 0.02:
            insights.append("Solid conversion rate demonstrates good audience-offer fit")
        
        if metrics.get("roi", 0) > 3.0:
            insights.append("Strong ROI indicates efficient campaign execution and high-quality audience")
        
        if not insights:
            insights.append("Campaign performed within expected parameters")
        
        return insights
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations for future campaigns."""
        logger.info("Generating recommendations for future campaigns")
        
        recommendations = []
        
        if metrics.get("open_rate", 0) < 0.20:
            recommendations.append("Test different subject lines to improve open rates")
        
        if metrics.get("click_rate", 0) < 0.06:
            recommendations.append("Refine CTA copy and design to increase engagement")
        
        if metrics.get("conversion_rate", 0) < 0.015:
            recommendations.append("Review landing page experience and offer relevance")
        
        recommendations.append("Conduct segment-level analysis to identify top performers")
        recommendations.append("Plan A/B tests for next campaign cycle")
        recommendations.append("Monitor competitive landscape for market changes")
        
        return recommendations