"""Base agent framework for all CrewAI agents."""
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog
import time

logger = structlog.get_logger(__name__)


class AgentInput(BaseModel):
    """Standardized input for all agents."""
    workflow_id: str = Field(..., description="Workflow identifier")
    campaign_id: Optional[str] = Field(None, description="Campaign identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class AgentOutput(BaseModel):
    """Standardized output for all agents."""
    status: str = Field(..., description="Execution status")
    message: str = Field(..., description="Status message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    execution_time_ms: float = Field(0, description="Execution time in milliseconds")


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.tools: List[Any] = []
        self.execution_count = 0
        
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
        logger.info("Tool added", agent=self.name, tool=tool)
    
    def log_execution_start(self, agent_input: AgentInput) -> None:
        """Log execution start."""
        logger.info("Agent execution started", agent=self.name, workflow_id=agent_input.workflow_id)
    
    def log_execution_end(self, execution_time_ms: float) -> None:
        """Log execution end."""
        self.execution_count += 1
        logger.info("Agent execution completed", agent=self.name, execution_time_ms=execution_time_ms, count=self.execution_count)
    
    @abstractmethod
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute the agent. Must be implemented by subclasses."""
        pass