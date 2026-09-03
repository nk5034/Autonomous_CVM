"""LangSmith integration utilities for workflow and agent observability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog

from src.core.config.settings import settings

logger = structlog.get_logger(__name__)

try:
    from langsmith import Client
except Exception:  # pragma: no cover - optional dependency guard
    Client = None  # type: ignore[assignment]


@dataclass
class _TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class LangSmithTracker:
    """Thin wrapper around LangSmith with graceful no-op behavior when disabled."""

    def __init__(self) -> None:
        self.enabled = bool(
            settings.LANGSMITH_TRACING
            and settings.LANGSMITH_API_KEY
            and Client is not None
        )
        self._client: Any | None = None

        if not self.enabled:
            logger.info(
                "LangSmith disabled",
                enabled=settings.LANGSMITH_TRACING,
                has_api_key=bool(settings.LANGSMITH_API_KEY),
                package_available=Client is not None,
            )
            return

        try:
            self._client = Client(
                api_key=settings.LANGSMITH_API_KEY,
                api_url=settings.LANGSMITH_ENDPOINT,
            )
            logger.info(
                "LangSmith client initialized",
                endpoint=settings.LANGSMITH_ENDPOINT,
                project=settings.LANGSMITH_PROJECT,
                environment=settings.LANGSMITH_ENV,
                release=settings.LANGSMITH_RELEASE,
            )
        except Exception as exc:  # pragma: no cover - SDK/runtime safety guard
            logger.warning("LangSmith initialization failed", error=str(exc))
            self.enabled = False
            self._client = None

    @staticmethod
    def _safe_call(target: Any, method_name: str, **kwargs: Any) -> Any | None:
        method = getattr(target, method_name, None)
        if not callable(method):
            return None
        try:
            return method(**kwargs)
        except TypeError:
            try:
                return method()
            except Exception:
                return None
        except Exception:
            return None

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(timezone.utc)

    def _create_run(
        self,
        run_type: str,
        name: str,
        workflow_id: str,
        campaign_id: int | str | None,
        inputs: dict[str, Any] | None,
        metadata: dict[str, Any] | None,
    ) -> str | None:
        if not self.enabled or self._client is None:
            return None

        run_id = str(uuid4())
        extra = {
            "metadata": {
                "workflow_id": workflow_id,
                "campaign_id": campaign_id,
                "environment": settings.LANGSMITH_ENV,
                "release": settings.LANGSMITH_RELEASE,
                **(metadata or {}),
            }
        }

        self._safe_call(
            self._client,
            "create_run",
            id=run_id,
            name=name,
            run_type=run_type,
            inputs=inputs or {},
            session_name=settings.LANGSMITH_PROJECT,
            start_time=self._now_utc(),
            extra=extra,
        )
        return run_id

    def _complete_run(
        self,
        run_id: str,
        outputs: dict[str, Any] | None,
        error_message: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled or self._client is None:
            return

        kwargs: dict[str, Any] = {
            "run_id": run_id,
            "end_time": self._now_utc(),
            "outputs": outputs or {},
        }
        if error_message:
            kwargs["error"] = error_message
        if metadata:
            kwargs["extra"] = {"metadata": metadata}

        self._safe_call(self._client, "update_run", **kwargs)

    def track_workflow_execution(
        self,
        workflow_id: str,
        campaign_id: int,
        event_name: str,
        status: str,
        latency_ms: float,
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track workflow and node-level execution lifecycle."""
        run_metadata = {
            "status": status,
            "latency_ms": latency_ms,
            **(metadata or {}),
        }
        run_id = self._create_run(
            run_type="chain",
            name=event_name,
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            inputs=input_data,
            metadata=run_metadata,
        )
        if run_id is None:
            return

        self._complete_run(
            run_id=run_id,
            outputs=output_data,
            error_message=error_message,
            metadata=run_metadata,
        )

    def track_agent_execution(
        self,
        workflow_id: str,
        campaign_id: int | str | None,
        agent_name: str,
        status: str,
        latency_ms: float,
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track individual agent execution."""
        payload_metadata = {
            "agent_name": agent_name,
            "status": status,
            "latency_ms": latency_ms,
            **(metadata or {}),
        }
        run_id = self._create_run(
            run_type="tool",
            name=f"agent.{agent_name}",
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            inputs=input_data,
            metadata=payload_metadata,
        )
        if run_id is None:
            return

        self._complete_run(
            run_id=run_id,
            outputs=output_data,
            error_message=error_message,
            metadata=payload_metadata,
        )

    def track_prompt_execution(
        self,
        workflow_id: str,
        campaign_id: int | str | None,
        agent_name: str,
        prompt_name: str,
        prompt_text: str,
        model: str,
        token_usage: _TokenUsage,
        latency_ms: float,
        output_data: dict[str, Any] | None = None,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track prompt execution and token consumption."""
        prompt_metadata = {
            "agent_name": agent_name,
            "model": model,
            "latency_ms": latency_ms,
            "token_usage": {
                "input_tokens": token_usage.input_tokens,
                "output_tokens": token_usage.output_tokens,
                "total_tokens": token_usage.total_tokens,
            },
            **(metadata or {}),
        }
        run_id = self._create_run(
            run_type="llm",
            name=prompt_name,
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            inputs={"prompt": prompt_text},
            metadata=prompt_metadata,
        )
        if run_id is None:
            return

        self._complete_run(
            run_id=run_id,
            outputs=output_data,
            error_message=error_message,
            metadata=prompt_metadata,
        )

    def track_approval_flow(
        self,
        workflow_id: str,
        campaign_id: int,
        node_name: str,
        decision: str,
        approver: str,
        latency_ms: float,
        comment: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Track approval lifecycle and decisions."""
        self.track_workflow_execution(
            workflow_id=workflow_id,
            campaign_id=campaign_id,
            event_name=f"approval.{node_name}",
            status=decision,
            latency_ms=latency_ms,
            input_data={"approver": approver, "comment": comment},
            output_data={"decision": decision},
            error_message=error_message,
            metadata={"flow": "approval"},
        )

    def flush(self) -> None:
        """LangSmith client does not require explicit flush for normal operation."""
        return


_tracker: LangSmithTracker | None = None


def get_langsmith_tracker() -> LangSmithTracker:
    """Get or initialize the global LangSmith tracker singleton."""
    global _tracker
    if _tracker is None:
        _tracker = LangSmithTracker()
    return _tracker
