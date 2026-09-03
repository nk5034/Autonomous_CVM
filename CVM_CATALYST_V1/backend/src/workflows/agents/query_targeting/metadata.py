"""Metadata Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import briefing_tool

logger = structlog.get_logger(__name__)


class MetadataAgent(BaseAgent):
    """Agent responsible for managing campaign metadata and data mappings."""
    
    def __init__(self, name: str = "Metadata", role: str = "metadata"):
        super().__init__(name, role)
        self.goal = "Manage campaign metadata and data mappings"
        self.backstory = "Data governance manager with deep expertise in metadata management and compliance. I ensure proper data classification, tagging, and compliance tracking."
        self.add_tool(briefing_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute metadata agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            campaign_data = agent_input.context.get("campaign_data", {})
            
            metadata = self._manage_metadata(campaign_data)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Metadata management completed", workflow_id=agent_input.workflow_id)
            
            return AgentOutput(
                status="success",
                message="Metadata management completed successfully",
                data={"metadata": metadata},
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Metadata management failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Metadata management failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _manage_metadata(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage campaign metadata and classifications."""
        logger.info("Managing campaign metadata")
        
        metadata = {
            "data_sources": [
                "customer_database",
                "behavioral_data",
                "purchase_history"
            ],
            "classifications": {
                "personally_identifiable_information": "pii",
                "customer_email": "pii",
                "customer_phone": "pii",
                "purchase_history": "sensitive",
                "demographic_data": "sensitive",
                "campaign_name": "public",
                "objective": "public"
            },
            "data_elements": {
                "customer_id": {
                    "type": "string",
                    "classification": "pii",
                    "sensitivity": "high"
                },
                "email": {
                    "type": "string",
                    "classification": "pii",
                    "sensitivity": "high"
                },
                "phone": {
                    "type": "string",
                    "classification": "pii",
                    "sensitivity": "high"
                },
                "purchase_count": {
                    "type": "integer",
                    "classification": "sensitive",
                    "sensitivity": "medium"
                },
                "segment": {
                    "type": "string",
                    "classification": "public",
                    "sensitivity": "low"
                }
            },
            "retention_policy": {
                "pii": "12_months",
                "sensitive": "24_months",
                "public": "indefinite"
            },
            "compliance_tags": [
                "gdpr",
                "ccpa",
                "data_minimization"
            ],
            "data_lineage": {
                "source": "customer_database",
                "transformations": [
                    "segmentation",
                    "anonymization"
                ],
                "destination": "campaign_system"
            },
            "created_at": datetime.now(UTC).isoformat()
        }
        
        return metadata