"""Deployment Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import deployment_tool

logger = structlog.get_logger(__name__)


class DeploymentAgent(BaseAgent):
    """Agent responsible for deploying approved campaigns to production channels."""
    
    def __init__(self, name: str = "Deployment", role: str = "deployment"):
        super().__init__(name, role)
        self.goal = "Deploy approved campaigns to production channels"
        self.backstory = "Operations specialist with deep expertise in campaign deployment. I manage deployment orchestration, monitoring, and troubleshooting to ensure successful go-live."
        self.add_tool(deployment_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute deployment agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            deployment_config = agent_input.context.get("deployment_config", {})
            campaign_id = agent_input.campaign_id or agent_input.context.get("campaign_id", "")
            
            deployment_result = self._deploy_campaign(deployment_config, campaign_id)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info(
                "Campaign deployment completed",
                campaign_id=campaign_id,
                deployment_id=deployment_result["deployment_id"],
                status=deployment_result["deployment_status"]
            )
            
            return AgentOutput(
                status="success",
                message="Campaign deployed successfully",
                data={
                    "deployment_id": deployment_result["deployment_id"],
                    "deployment_status": deployment_result["deployment_status"],
                    "deployment_summary": deployment_result["deployment_summary"],
                    "channels_deployed": deployment_result["channels_deployed"],
                    "audience_size": deployment_result["audience_size"]
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Campaign deployment failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Campaign deployment failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _deploy_campaign(self, deployment_config: Dict[str, Any], campaign_id: str) -> Dict[str, Any]:
        """Deploy campaign to production."""
        logger.info("Deploying campaign to production", campaign_id=campaign_id)
        
        deployment_result = deployment_tool.deploy_campaign(deployment_config)
        
        channels = deployment_config.get("channels", ["email", "sms", "push"])
        
        return {
            "deployment_id": deployment_result["deployment_id"],
            "deployment_status": deployment_result["status"],
            "campaign_id": campaign_id,
            "channels_deployed": channels,
            "audience_size": deployment_result.get("audience_size", 50000),
            "deployment_summary": {
                "total_channels": len(channels),
                "channels": channels,
                "deployment_timestamp": deployment_result["timestamp"],
                "monitoring_enabled": True
            },
            "deployed_at": datetime.now(UTC).isoformat()
        }