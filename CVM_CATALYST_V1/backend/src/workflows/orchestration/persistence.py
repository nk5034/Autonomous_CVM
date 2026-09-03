"""File-based state persistence and checkpointing for workflow runs."""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from src.workflows.orchestration.state import CampaignState


class WorkflowStateStore:
    """Persists the latest state for each workflow run."""

    def __init__(self, base_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[4]
        self.base_dir = base_dir or root / "backend" / "logs" / "workflow_state"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, workflow_id: str) -> Path:
        safe_workflow_id = _validate_identifier(workflow_id, field_name="workflow_id")
        return self.base_dir / f"{safe_workflow_id}.json"

    def save_state(self, state: CampaignState) -> None:
        path = self._state_path(state.workflow_id)
        path.write_text(
            json.dumps(state.to_dict(), indent=2, sort_keys=True, ensure_ascii=True),
            encoding="utf-8",
        )

    def load_state(self, workflow_id: str) -> CampaignState | None:
        path = self._state_path(workflow_id)
        if not path.exists():
            return None
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return CampaignState.from_dict(data)

    def list_workflows(self) -> list[str]:
        return sorted(item.stem for item in self.base_dir.glob("*.json"))


class WorkflowCheckpointStore:
    """Stores immutable snapshots for replay and resume support."""

    def __init__(self, base_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[4]
        self.base_dir = base_dir or root / "backend" / "logs" / "workflow_checkpoints"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _workflow_dir(self, workflow_id: str) -> Path:
        safe_workflow_id = _validate_identifier(workflow_id, field_name="workflow_id")
        directory = self.base_dir / safe_workflow_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def create_checkpoint(self, state: CampaignState, label: str | None = None) -> str:
        checkpoint_id = f"{label or 'checkpoint'}-{uuid4().hex[:12]}"
        checkpoint_path = self._workflow_dir(state.workflow_id) / f"{checkpoint_id}.json"
        payload = {
            "checkpoint_id": checkpoint_id,
            "label": label,
            "state": state.to_dict(),
        }
        checkpoint_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True),
            encoding="utf-8",
        )
        state.checkpoint_ids.append(checkpoint_id)
        return checkpoint_id

    def load_checkpoint(self, workflow_id: str, checkpoint_id: str) -> CampaignState | None:
        safe_checkpoint_id = _validate_identifier(checkpoint_id, field_name="checkpoint_id")
        checkpoint_path = self._workflow_dir(workflow_id) / f"{safe_checkpoint_id}.json"
        if not checkpoint_path.exists():
            return None
        payload: dict[str, Any] = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        return CampaignState.from_dict(payload["state"])

    def list_checkpoints(self, workflow_id: str) -> list[str]:
        workflow_dir = self._workflow_dir(workflow_id)
        return sorted(item.stem for item in workflow_dir.glob("*.json"))


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


def _validate_identifier(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")
    if not _ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"Invalid {field_name}. Use 1-128 chars from [A-Za-z0-9_.:-] and start with alphanumeric."
        )
    return normalized

