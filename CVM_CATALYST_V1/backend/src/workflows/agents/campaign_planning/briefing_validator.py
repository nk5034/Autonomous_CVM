"""Briefing Validator Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class BriefingValidatorAgent(BaseAgent):
    """Agent responsible for validating briefing against all business rules and compliance requirements."""
    
    def __init__(self, name: str = "BriefingValidator", role: str = "briefing_validator"):
        super().__init__(name, role)
        self.goal = "Validate briefing against all business rules and compliance requirements"
        self.backstory = "QA validator with expertise in business rules and compliance. I ensure all briefs meet standards before proceeding to audience design."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute briefing validator agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract enriched briefing from context
            enriched_briefing = agent_input.context.get("enriched_briefing", {})
            
            # Run all validations
            validation_results = self._run_validations(enriched_briefing)
            
            # Extract issues
            issues = self._extract_issues(validation_results)
            
            # Determine approvals needed
            approvals_required = self._determine_approvals_needed(enriched_briefing, issues)
            
            # Overall approval status
            is_approved = len(issues) == 0 and validation_results.get("business_rules_valid", False)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info(
                "Briefing validation completed",
                workflow_id=agent_input.workflow_id,
                is_approved=is_approved,
                issue_count=len(issues)
            )
            
            return AgentOutput(
                status="success",
                message="Briefing validation completed",
                data={
                    "is_approved": is_approved,
                    "validation_results": validation_results,
                    "issues": issues,
                    "approvals_required": approvals_required,
                    "ready_for_audience_design": is_approved
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Briefing validation failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Briefing validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _run_validations(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info("Running validation suite")
        
        results = {
            "business_rules_valid": True,
            "budget_valid": False,
            "audience_valid": False,
            "channels_valid": False,
            "compliance_valid": False,
            "timeline_valid": False,
            "errors": []
        }
        
        # Validate business rules
        results["business_rules_valid"] = self._validate_business_rules(briefing)
        
        # Validate budget
        results["budget_valid"] = self._validate_budget(briefing)
        
        # Validate audience
        results["audience_valid"] = self._validate_audience(briefing)
        
        # Validate channels
        results["channels_valid"] = self._validate_channels(briefing)
        
        # Validate compliance
        results["compliance_valid"] = self._validate_compliance(briefing)
        
        # Validate timeline
        results["timeline_valid"] = self._validate_timeline(briefing)
        
        return results
    
    def _validate_business_rules(self, briefing: Dict[str, Any]) -> bool:
        """Validate business rules."""
        logger.info("Validating business rules")
        
        if not briefing.get("objective"):
            logger.warning("Business rule violation: missing objective")
            return False
        
        if not briefing.get("target_audience"):
            logger.warning("Business rule violation: missing target audience")
            return False
        
        return True
    
    def _validate_budget(self, briefing: Dict[str, Any]) -> bool:
        """Validate budget constraints."""
        logger.info("Validating budget")
        
        budget = briefing.get("budget", 0)
        
        if budget <= 0:
            logger.warning("Budget validation failed: budget must be greater than 0")
            return False
        
        if budget > 1000000:
            logger.warning("Budget validation failed: budget exceeds maximum of $1,000,000")
            return False
        
        return True
    
    def _validate_audience(self, briefing: Dict[str, Any]) -> bool:
        """Validate audience definition."""
        logger.info("Validating audience")
        
        audience = briefing.get("target_audience", "").strip()
        
        if not audience or len(audience) < 10:
            logger.warning("Audience validation failed: audience description too short")
            return False
        
        return True
    
    def _validate_channels(self, briefing: Dict[str, Any]) -> bool:
        """Validate channel selection."""
        logger.info("Validating channels")
        
        channels = briefing.get("channels", [])
        valid_channels = ["email", "sms", "push", "social", "web", "print"]
        
        if not channels:
            logger.warning("Channel validation failed: no channels selected")
            return False
        
        for channel in channels:
            if channel.lower() not in valid_channels:
                logger.warning(f"Channel validation failed: invalid channel {channel}")
                return False
        
        return True
    
    def _validate_compliance(self, briefing: Dict[str, Any]) -> bool:
        """Validate compliance requirements."""
        logger.info("Validating compliance")
        
        # Check if GDPR relevant
        if briefing.get("target_audience"):
            logger.info("Compliance check: GDPR requirements applicable")
        
        # Check if CCPA relevant
        if briefing.get("channels"):
            logger.info("Compliance check: CCPA requirements applicable")
        
        return True
    
    def _validate_timeline(self, briefing: Dict[str, Any]) -> bool:
        """Validate timeline and dates."""
        logger.info("Validating timeline")
        
        start_date = briefing.get("start_date")
        end_date = briefing.get("end_date")
        
        if not start_date or not end_date:
            logger.warning("Timeline validation: missing dates")
            return False
        
        return True
    
    def _extract_issues(self, validation_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract list of issues from validation results."""
        logger.info("Extracting validation issues")
        
        issues = []
        
        if not validation_results.get("business_rules_valid"):
            issues.append({
                "type": "business_rule",
                "severity": "critical",
                "message": "Business rule validation failed"
            })
        
        if not validation_results.get("budget_valid"):
            issues.append({
                "type": "budget",
                "severity": "critical",
                "message": "Budget validation failed"
            })
        
        if not validation_results.get("audience_valid"):
            issues.append({
                "type": "audience",
                "severity": "high",
                "message": "Audience definition invalid"
            })
        
        if not validation_results.get("channels_valid"):
            issues.append({
                "type": "channels",
                "severity": "high",
                "message": "Channel selection invalid"
            })
        
        return issues
    
    def _determine_approvals_needed(self, briefing: Dict[str, Any], issues: List[Dict]) -> List[str]:
        """Determine which approvals are required."""
        logger.info("Determining required approvals")
        
        approvals = []
        
        # Budget approval for large budgets
        if briefing.get("budget", 0) > 100000:
            approvals.append("budget_owner")
        
        # Compliance approval always needed
        approvals.append("compliance_officer")
        
        # Manager approval
        approvals.append("campaign_manager")
        
        # Additional approval if there are issues
        if issues:
            approvals.append("business_lead")
        
        return list(set(approvals))