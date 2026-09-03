"""Approval Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class ApprovalAgent(BaseAgent):
    """Agent responsible for managing approval workflows and compliance checks."""
    
    def __init__(self, name: str = "Approval", role: str = "approval"):
        super().__init__(name, role)
        self.goal = "Manage approval workflows and compliance checks"
        self.backstory = "Workflow and compliance manager with deep expertise in governance. I ensure proper approval chains are followed and all compliance requirements are met."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute approval agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            campaign_summary = agent_input.context.get("campaign_summary", {})
            approvers_required = agent_input.context.get("approvers_required", [])
            
            approval_workflow = self._manage_approval_workflow(campaign_summary, approvers_required)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info(
                "Approval workflow setup completed",
                workflow_id=agent_input.workflow_id,
                approval_count=len(approval_workflow["required_approvals"])
            )
            
            return AgentOutput(
                status="success",
                message="Approval workflow configured successfully",
                data={
                    "approval_workflow_id": approval_workflow["approval_workflow_id"],
                    "required_approvals": approval_workflow["required_approvals"],
                    "escalation_required": approval_workflow["escalation_required"],
                    "approval_deadline": approval_workflow["approval_deadline"]
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Approval workflow setup failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Approval workflow setup failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _manage_approval_workflow(self, campaign_summary: Dict[str, Any], approvers: List[str]) -> Dict[str, Any]:
        """Manage approval workflow."""
        logger.info("Managing approval workflow")
        
        workflow_id = f"approval_{int(datetime.now(UTC).timestamp())}"
        
        required_approvals = [
            {
                "approver_id": "manager",
                "approver_role": "Campaign Manager",
                "status": "pending",
                "required": True,
                "deadline_days": 2
            },
            {
                "approver_id": "compliance",
                "approver_role": "Compliance Officer",
                "status": "pending",
                "required": True,
                "deadline_days": 2
            },
            {
                "approver_id": "budget_owner",
                "approver_role": "Budget Owner",
                "status": "pending",
                "required": campaign_summary.get("budget", 0) > 100000,
                "deadline_days": 1
            }
        ]
        
        # Filter to include only required approvals
        required_approvals = [a for a in required_approvals if a["required"]]
        
        escalation_required = len(required_approvals) > 2
        
        return {
            "approval_workflow_id": workflow_id,
            "required_approvals": required_approvals,
            "escalation_required": escalation_required,
            "approval_deadline": "2024-01-10T17:00:00Z",
            "created_at": datetime.now(UTC).isoformat()
        }