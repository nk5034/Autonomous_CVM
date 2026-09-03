"""AB Testing Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import test_tool

logger = structlog.get_logger(__name__)


class ABTestingAgent(BaseAgent):
    """Agent responsible for configuring AB testing for campaign optimization."""
    
    def __init__(self, name: str = "ABTesting", role: str = "ab_testing"):
        super().__init__(name, role)
        self.goal = "Configure AB testing for campaign optimization"
        self.backstory = "AB testing specialist with deep expertise in experimental design. I design rigorous tests with proper statistical rigor to optimize campaign performance."
        self.add_tool(test_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute AB testing agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            campaign_design = agent_input.context.get("campaign_design", {})
            
            test_config = self._configure_ab_testing(campaign_design)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("AB testing configuration completed", workflow_id=agent_input.workflow_id)
            
            return AgentOutput(
                status="success",
                message="AB testing configuration completed successfully",
                data={
                    "test_configuration": test_config["configuration"],
                    "test_variants": test_config["variants"],
                    "sample_sizes": test_config["sample_sizes"],
                    "duration_days": test_config["duration_days"]
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("AB testing configuration failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"AB testing configuration failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _configure_ab_testing(self, campaign_design: Dict[str, Any]) -> Dict[str, Any]:
        """Configure AB testing for campaign."""
        logger.info("Configuring AB testing")
        
        configuration = {
            "test_type": "multivariate",
            "confidence_level": 0.95,
            "statistical_power": 0.80,
            "duration_days": 14,
            "minimum_sample_size": 5000,
            "hypothesis": "Treatment variants will outperform control"
        }
        
        variants = [
            {
                "variant_id": "control",
                "name": "Control",
                "description": "Original campaign design",
                "allocation_percentage": 33.3
            },
            {
                "variant_id": "variant_1",
                "name": "Variant 1 - Optimized Copy",
                "description": "Enhanced value proposition messaging",
                "allocation_percentage": 33.3
            },
            {
                "variant_id": "variant_2",
                "name": "Variant 2 - Premium Treatment",
                "description": "Premium design elements and exclusive tone",
                "allocation_percentage": 33.4
            }
        ]
        
        total_audience = campaign_design.get("total_audience", 100000)
        sample_size_per_variant = int(total_audience / 3)
        
        sample_sizes = {
            "control": sample_size_per_variant,
            "variant_1": sample_size_per_variant,
            "variant_2": sample_size_per_variant,
            "total": total_audience
        }
        
        return {
            "configuration": configuration,
            "variants": variants,
            "sample_sizes": sample_sizes,
            "duration_days": 14,
            "created_at": datetime.now(UTC).isoformat()
        }