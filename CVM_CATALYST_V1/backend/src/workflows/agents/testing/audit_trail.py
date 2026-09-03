"""Audit trail service for Phase 7 testing platform."""
from datetime import UTC, datetime
import hashlib
from typing import Any, Dict, List, Optional

from src.workflows.agents.testing.platform_models import AuditTrailEntry


class AuditTrailManager:
    """Maintains immutable event trail for test execution accountability."""

    def __init__(self) -> None:
        self._entries: List[AuditTrailEntry] = []
        self._counter = 0

    def record(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        correlation_id: Optional[str] = None,
    ) -> AuditTrailEntry:
        """Record a new audit event with chained checksum."""
        self._counter += 1
        event_id = f"audit_{self._counter:06d}"
        previous_hash = self._entries[-1].checksum if self._entries else "ROOT"

        payload = f"{event_id}|{action}|{actor}|{previous_hash}|{datetime.now(UTC).isoformat()}|{details or {}}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        entry = AuditTrailEntry(
            event_id=event_id,
            action=action,
            actor=actor,
            details=details or {},
            correlation_id=correlation_id,
            checksum=checksum,
        )
        self._entries.append(entry)
        return entry

    def list_entries(self) -> List[AuditTrailEntry]:
        """Return all audit entries."""
        return list(self._entries)
