"""Agent observability for monitoring, metrics, and alerting."""
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
import structlog
import time

logger = structlog.get_logger(__name__)


class MetricType(str, Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class Metric(BaseModel):
    """A single metric data point."""
    metric_id: str = Field(..., description="Unique metric ID")
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Metric type")
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    model_config = ConfigDict(use_enum_values=True)


class Event(BaseModel):
    """A single event log entry."""
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    message: str = Field(..., description="Event message")
    severity: str = Field(..., description="Event severity")
    tags: Dict[str, str] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class Alert(BaseModel):
    """An alert entry."""
    alert_id: str = Field(..., description="Unique alert ID")
    alert_type: str = Field(..., description="Alert type")
    message: str = Field(..., description="Alert message")
    severity: str = Field(..., description="Severity level")
    threshold_value: float = Field(..., description="Threshold that triggered alert")
    actual_value: float = Field(..., description="Actual value that triggered alert")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class AgentObservability:
    """Monitor and observe agent execution metrics, events, and alerts."""
    
    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._events: List[Event] = []
        self._alerts: List[Alert] = []
        self._performance_data: Dict[str, List[float]] = {}
        self._counter = 0
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Record a single metric."""
        metric_id = f"metric_{self._counter}_{int(time.time() * 1000)}"
        self._counter += 1
        
        metric = Metric(
            metric_id=metric_id,
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {}
        )
        
        self._metrics[metric_id] = metric
        logger.info("Metric recorded", metric_name=name, value=value, metric_type=metric_type.value)
        return metric_id
    
    def record_event(
        self,
        event_type: str,
        message: str,
        severity: str = "info",
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Record an event."""
        event_id = f"event_{self._counter}_{int(time.time() * 1000)}"
        self._counter += 1
        
        event = Event(
            event_id=event_id,
            event_type=event_type,
            message=message,
            severity=severity,
            tags=tags or {}
        )
        
        self._events.append(event)
        logger.info("Event recorded", event_type=event_type, severity=severity, message=message)
        return event_id
    
    def record_alert(
        self,
        alert_type: str,
        message: str,
        severity: str,
        threshold_value: float,
        actual_value: float
    ) -> str:
        """Record an alert."""
        alert_id = f"alert_{self._counter}_{int(time.time() * 1000)}"
        self._counter += 1
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            message=message,
            severity=severity,
            threshold_value=threshold_value,
            actual_value=actual_value
        )
        
        self._alerts.append(alert)
        logger.warning("Alert recorded", alert_type=alert_type, severity=severity, message=message)
        return alert_id
    
    def record_performance(
        self,
        agent_name: str,
        execution_time_ms: float
    ) -> None:
        """Record performance data."""
        if agent_name not in self._performance_data:
            self._performance_data[agent_name] = []
        
        self._performance_data[agent_name].append(execution_time_ms)
        logger.info("Performance recorded", agent=agent_name, execution_time_ms=execution_time_ms)
    
    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """Get metrics, optionally filtered by name."""
        if name:
            return [m for m in self._metrics.values() if m.name == name]
        return list(self._metrics.values())
    
    def get_events(self, event_type: Optional[str] = None) -> List[Event]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self._events if e.event_type == event_type]
        return self._events.copy()
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """Get alerts, optionally filtered by severity."""
        if severity:
            return [a for a in self._alerts if a.severity == severity]
        return self._alerts.copy()
    
    def get_performance_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        
        if agent_name:
            times = self._performance_data.get(agent_name, [])
            if times:
                stats = {
                    "agent": agent_name,
                    "count": len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "avg_ms": sum(times) / len(times),
                    "total_ms": sum(times)
                }
        else:
            for agent, times in self._performance_data.items():
                if times:
                    stats[agent] = {
                        "count": len(times),
                        "min_ms": min(times),
                        "max_ms": max(times),
                        "avg_ms": sum(times) / len(times)
                    }
        
        return stats
    
    def get_observability_report(self) -> Dict[str, Any]:
        """Generate comprehensive observability report."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics_count": len(self._metrics),
            "events_count": len(self._events),
            "alerts_count": len(self._alerts),
            "performance_agents": len(self._performance_data),
            "performance_stats": self.get_performance_stats(),
            "recent_alerts": [a.model_dump() for a in self._alerts[-5:]] if self._alerts else [],
            "recent_events": [e.model_dump() for e in self._events[-5:]] if self._events else []
        }
    
    def clear(self) -> None:
        """Clear all observability data (for testing)."""
        self._metrics.clear()
        self._events.clear()
        self._alerts.clear()
        self._performance_data.clear()
        logger.info("Observability data cleared")