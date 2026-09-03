"""Test Scenario Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import test_tool

logger = structlog.get_logger(__name__)


class TestScenarioAgent(BaseAgent):
    """Agent responsible for creating comprehensive test scenarios for campaigns."""
    __test__ = False
    
    def __init__(self, name: str = "TestScenario", role: str = "test_scenario"):
        super().__init__(name, role)
        self.goal = "Create comprehensive test scenarios for campaigns"
        self.backstory = "QA strategist with deep expertise in test design. I create comprehensive scenarios that validate campaign logic, performance, and edge cases."
        self.add_tool(test_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute test scenario agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            campaign_design = agent_input.context.get("campaign_design", {})
            
            scenarios = self._create_scenarios(campaign_design)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Test scenario creation completed", workflow_id=agent_input.workflow_id, scenario_count=len(scenarios))
            
            return AgentOutput(
                status="success",
                message="Test scenarios created successfully",
                data={
                    "test_scenarios": scenarios,
                    "scenario_count": len(scenarios)
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Test scenario creation failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Test scenario creation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _create_scenarios(self, campaign_design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create test scenarios for campaign."""
        logger.info("Creating test scenarios")
        
        scenarios_dict = test_tool.create_test_scenario(campaign_design)
        
        scenarios = []
        for scenario_id, scenario_data in scenarios_dict.items():
            scenarios.append({
                "scenario_id": scenario_data["scenario_id"],
                "name": scenario_data["name"],
                "description": scenario_data["description"],
                "expected_result": scenario_data["expected_result"],
                "priority": self._determine_priority(scenario_data["name"])
            })
        
        return scenarios
    
    def _determine_priority(self, scenario_name: str) -> str:
        """Determine scenario priority."""
        scenario_name_lower = scenario_name.lower()
        
        if "happy" in scenario_name_lower:
            return "critical"
        elif "high" in scenario_name_lower:
            return "high"
        elif "edge" in scenario_name_lower:
            return "medium"
        elif "failure" in scenario_name_lower:
            return "high"
        else:
            return "medium"