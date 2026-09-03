"""Agent execution manager for orchestrating agent lifecycle."""
from datetime import UTC, datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
import structlog
import asyncio
import time

from src.workflows.observability.langsmith import _TokenUsage, get_langsmith_tracker

logger = structlog.get_logger(__name__)


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ExecutionRecord(BaseModel):
    """Record of a single agent execution."""
    execution_id: str = Field(..., description="Unique execution ID")
    agent_id: str = Field(..., description="Agent identifier")
    status: ExecutionStatus = Field(..., description="Execution status")
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    execution_time_ms: float = Field(0, description="Execution time in milliseconds")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    model_config = ConfigDict(use_enum_values=True)


class AgentExecutionManager:
    """Manages agent execution lifecycle and history."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._execution_history: Dict[str, ExecutionRecord] = {}
        self._active_executions: Dict[str, asyncio.Task] = {}
        self._execution_counter = 0
        self._langsmith = get_langsmith_tracker()

    @staticmethod
    def _extract_token_usage(output_data: Dict[str, Any]) -> _TokenUsage:
        """Extract token usage from flexible output schemas."""
        candidates = [
            output_data.get("token_usage"),
            output_data.get("usage"),
            output_data.get("data", {}).get("token_usage") if isinstance(output_data.get("data"), dict) else None,
            output_data.get("data", {}).get("usage") if isinstance(output_data.get("data"), dict) else None,
        ]

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            input_tokens = int(candidate.get("input_tokens", candidate.get("prompt_tokens", 0)) or 0)
            output_tokens = int(candidate.get("output_tokens", candidate.get("completion_tokens", 0)) or 0)
            total_tokens = int(candidate.get("total_tokens", input_tokens + output_tokens) or 0)
            return _TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )

        return _TokenUsage()

    @staticmethod
    def _extract_prompt(agent_input: Any) -> tuple[str | None, str | None]:
        """Extract prompt metadata from AgentInput context."""
        context = getattr(agent_input, "context", None)
        if not isinstance(context, dict):
            return None, None

        prompt_text = context.get("prompt") or context.get("prompt_text")
        if prompt_text is None:
            user_prompt = context.get("user_prompt")
            system_prompt = context.get("system_prompt")
            if user_prompt or system_prompt:
                prompt_text = f"system:{system_prompt or ''}\nuser:{user_prompt or ''}".strip()

        prompt_name = context.get("prompt_name") or "agent_prompt"
        return (str(prompt_name) if prompt_text else None, str(prompt_text) if prompt_text else None)
    
    async def execute_agent(
        self,
        agent,
        agent_input: Any,
        timeout: Optional[int] = None
    ) -> ExecutionRecord:
        """Execute a single agent with timeout protection."""
        execution_id = f"exec_{self._execution_counter}_{int(time.time() * 1000)}"
        self._execution_counter += 1
        
        record = ExecutionRecord(
            execution_id=execution_id,
            agent_id=getattr(agent, 'name', 'unknown'),
            status=ExecutionStatus.PENDING,
            input_data=agent_input.model_dump() if hasattr(agent_input, "model_dump") else {}
        )

        workflow_id = record.input_data.get("workflow_id", "unknown")
        campaign_id = record.input_data.get("campaign_id")
        start_time = time.perf_counter()
        output_data: Dict[str, Any] = {}
        error_message: str | None = None
        current_task = asyncio.current_task()
        
        try:
            async with self._semaphore:
                if current_task is not None:
                    self._active_executions[execution_id] = current_task

                record.status = ExecutionStatus.RUNNING
                self._execution_history[execution_id] = record

                logger.info("Agent execution started", execution_id=execution_id, agent=record.agent_id)

                start_time = time.perf_counter()

                # Execute with timeout
                if timeout:
                    result = await asyncio.wait_for(agent.execute(agent_input), timeout=timeout)
                else:
                    result = await agent.execute(agent_input)

                execution_time_ms = (time.perf_counter() - start_time) * 1000

                record.status = ExecutionStatus.COMPLETED
                record.completed_at = datetime.now(UTC).isoformat()
                record.execution_time_ms = execution_time_ms
                output_data = result.model_dump() if hasattr(result, "model_dump") else {}
                record.output_data = output_data

                logger.info("Agent execution completed", execution_id=execution_id, time_ms=execution_time_ms)
            
        except asyncio.TimeoutError:
            record.status = ExecutionStatus.FAILED
            record.error_message = f"Execution timeout after {timeout}s"
            error_message = record.error_message
            logger.error("Agent execution timeout", execution_id=execution_id, timeout=timeout)
        except Exception as e:
            record.status = ExecutionStatus.FAILED
            record.error_message = str(e)
            error_message = str(e)
            logger.error("Agent execution failed", execution_id=execution_id, error=str(e))
        finally:
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if record.execution_time_ms <= 0:
                record.execution_time_ms = elapsed_ms

            self._langsmith.track_agent_execution(
                workflow_id=workflow_id,
                campaign_id=campaign_id,
                agent_name=record.agent_id,
                status=record.status.value if isinstance(record.status, ExecutionStatus) else str(record.status),
                latency_ms=record.execution_time_ms,
                input_data=record.input_data,
                output_data=output_data or record.output_data,
                error_message=error_message,
                metadata={"execution_id": execution_id},
            )

            prompt_name, prompt_text = self._extract_prompt(agent_input)
            if prompt_name and prompt_text:
                self._langsmith.track_prompt_execution(
                    workflow_id=workflow_id,
                    campaign_id=campaign_id,
                    agent_name=record.agent_id,
                    prompt_name=prompt_name,
                    prompt_text=prompt_text,
                    model=(record.input_data.get("context") or {}).get("model", "unknown"),
                    token_usage=self._extract_token_usage(output_data or record.output_data),
                    latency_ms=record.execution_time_ms,
                    output_data=output_data or record.output_data,
                    error_message=error_message,
                    metadata={"execution_id": execution_id},
                )
        
        return record
    
    async def execute_sequential(
        self,
        agents: List,
        agent_input: Any
    ) -> List[ExecutionRecord]:
        """Execute agents sequentially."""
        records = []
        current_input = agent_input
        
        for agent in agents:
            record = await self.execute_agent(agent, current_input)
            records.append(record)
            
            if record.status == ExecutionStatus.FAILED:
                logger.warning("Sequential execution stopped due to failure", agent=agent.name)
                break
        
        return records
    
    def get_execution_record(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get a specific execution record."""
        return self._execution_history.get(execution_id)
    
    def get_execution_history(self, agent_id: Optional[str] = None) -> List[ExecutionRecord]:
        """Get execution history, optionally filtered by agent."""
        if agent_id:
            return [r for r in self._execution_history.values() if r.agent_id == agent_id]
        return list(self._execution_history.values())
    
    def get_active_executions(self) -> List[ExecutionRecord]:
        """Get currently active executions."""
        return [
            r for r in self._execution_history.values() 
            if r.status == ExecutionStatus.RUNNING
        ]
    
    def clear_history(self) -> None:
        """Clear execution history (for testing)."""
        self._execution_history.clear()
        logger.info("Execution history cleared")