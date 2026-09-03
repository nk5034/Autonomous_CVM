"""Query Builder Agent for campaign workflow."""
from typing import Dict, Any, List
from datetime import UTC, datetime
import structlog
from src.workflows.agents.base import BaseAgent, AgentInput, AgentOutput
from src.workflows.agents.tools import query_tool

logger = structlog.get_logger(__name__)


class QueryBuilderAgent(BaseAgent):
    """Agent responsible for building audience queries for targeting and selection."""
    
    def __init__(self, name: str = "QueryBuilder", role: str = "query_builder"):
        super().__init__(name, role)
        self.goal = "Build audience queries for targeting and selection"
        self.backstory = "Data query specialist with SQL expertise. I convert audience segment definitions into executable queries for audience selection and targeting."
        self.add_tool(query_tool)
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute query builder agent."""
        self.log_execution_start(agent_input)
        
        try:
            start_time = datetime.now(UTC)
            
            # Extract segment definitions from context
            segment_definitions = agent_input.context.get("segment_definitions", {})
            
            # Build queries for each segment
            queries = {}
            for segment_id, definition in segment_definitions.items():
                query = query_tool.build_query(definition)
                queries[segment_id] = {
                    "segment_id": segment_id,
                    "segment_name": definition.get("segment_name", ""),
                    "query": query,
                    "query_type": "sql"
                }
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.log_execution_end(execution_time)
            
            logger.info("Query building completed", workflow_id=agent_input.workflow_id, query_count=len(queries))
            
            return AgentOutput(
                status="success",
                message="Audience queries built successfully",
                data={
                    "queries": queries,
                    "query_count": len(queries),
                    "ready_for_execution": True
                },
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error("Query building failed", error=str(e))
            return AgentOutput(
                status="failed",
                message=f"Query building failed: {str(e)}",
                errors=[str(e)]
            )