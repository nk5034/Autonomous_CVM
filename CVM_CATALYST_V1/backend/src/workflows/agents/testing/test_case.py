"""Test Case Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import test_tool

logger = structlog.get_logger(__name__)


class TestCaseAgent(BaseAgent):
    """Agent responsible for generating detailed test cases from scenarios."""
    __test__ = False
    
    def __init__(self, name: str = "TestCase", role: str = "test_case"):
        super().__init__(name, role)
        self.goal = "Generate detailed test cases from scenarios"
        self.backstory = "Test automation engineer with deep expertise in test case design. I convert scenarios into executable test cases with clear steps and expected outcomes."
        self.add_tool(test_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute test case agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            test_scenarios = agent_input.context.get("test_scenarios", [])
            
            test_cases = self._generate_test_cases(test_scenarios)
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Test case generation completed", workflow_id=agent_input.workflow_id, case_count=len(test_cases))
            
            return AgentOutput(
                status="success",
                message="Test cases generated successfully",
                data={
                    "test_cases": test_cases,
                    "test_case_count": len(test_cases)
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Test case generation failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Test case generation failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _generate_test_cases(self, scenarios: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate test cases from scenarios."""
        logger.info("Generating test cases from scenarios")
        
        test_cases = {}
        
        for scenario in scenarios:
            scenario_id = scenario.get("scenario_id", "")
            scenario_name = scenario.get("name", "")
            
            cases = self._create_cases_for_scenario(scenario_id, scenario_name)
            test_cases[scenario_id] = cases
        
        return test_cases
    
    def _create_cases_for_scenario(self, scenario_id: str, scenario_name: str) -> List[Dict[str, Any]]:
        """Create test cases for a specific scenario."""
        logger.info("Creating test cases for scenario", scenario_name=scenario_name)
        
        cases = []
        
        if "happy" in scenario_name.lower():
            cases = [
                {
                    "case_id": f"{scenario_id}_001",
                    "title": "Valid campaign deployment",
                    "steps": [
                        "Load campaign configuration",
                        "Validate all required fields",
                        "Execute deployment process",
                        "Verify deployment status"
                    ],
                    "expected": "Campaign deploys successfully with status = deployed"
                },
                {
                    "case_id": f"{scenario_id}_002",
                    "title": "Successful audience targeting",
                    "steps": [
                        "Load audience segments",
                        "Execute queries for each segment",
                        "Verify audience counts",
                        "Confirm segmentation"
                    ],
                    "expected": "All segments targeted correctly with accurate counts"
                }
            ]
        elif "high" in scenario_name.lower() and "volume" in scenario_name.lower():
            cases = [
                {
                    "case_id": f"{scenario_id}_001",
                    "title": "Handle maximum audience load",
                    "steps": [
                        "Load campaign with 1M+ audience",
                        "Monitor system performance",
                        "Execute all processing steps",
                        "Verify completion time < 5 minutes"
                    ],
                    "expected": "System handles high volume without degradation"
                }
            ]
        elif "edge" in scenario_name.lower():
            cases = [
                {
                    "case_id": f"{scenario_id}_001",
                    "title": "Handle empty audience segment",
                    "steps": [
                        "Create segment with zero size",
                        "Attempt to target",
                        "Verify error handling"
                    ],
                    "expected": "System gracefully handles empty segment"
                },
                {
                    "case_id": f"{scenario_id}_002",
                    "title": "Handle maximum budget constraint",
                    "steps": [
                        "Set budget to $1,000,000 limit",
                        "Execute campaign",
                        "Verify compliance"
                    ],
                    "expected": "Campaign respects budget boundary"
                }
            ]
        elif "failure" in scenario_name.lower():
            cases = [
                {
                    "case_id": f"{scenario_id}_001",
                    "title": "Recover from deployment failure",
                    "steps": [
                        "Trigger deployment failure",
                        "Execute recovery process",
                        "Verify data integrity",
                        "Resume campaign"
                    ],
                    "expected": "System recovers without data loss"
                }
            ]
        else:
            cases = []

        return cases