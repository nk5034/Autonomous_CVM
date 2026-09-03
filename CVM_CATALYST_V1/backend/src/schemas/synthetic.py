"""Schemas for Phase 8 synthetic data generation APIs."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SyntheticVolumeConfig(BaseModel):
    """Configurable generation controls for synthetic datasets."""

    customer_count: int = Field(default=1000, ge=10, le=200000)
    household_coverage_ratio: float = Field(default=0.45, ge=0.1, le=1.0)
    avg_subscriptions_per_customer: float = Field(default=1.2, ge=0.0, le=5.0)
    avg_interactions_per_customer: int = Field(default=6, ge=0, le=200)
    channel_response_rate: float = Field(default=0.28, ge=0.0, le=1.0)
    conversion_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    record_overrides: dict[str, int] = Field(default_factory=dict)


class SyntheticDataPayload(BaseModel):
    """Synthetic datasets grouped by domain."""

    customer_data: list[dict[str, Any]] = Field(default_factory=list)
    subscription_data: list[dict[str, Any]] = Field(default_factory=list)
    household_data: list[dict[str, Any]] = Field(default_factory=list)
    revenue_data: list[dict[str, Any]] = Field(default_factory=list)
    interaction_history: list[dict[str, Any]] = Field(default_factory=list)
    scores: list[dict[str, Any]] = Field(default_factory=list)
    channel_responses: list[dict[str, Any]] = Field(default_factory=list)


class SyntheticDataGenerationRequest(BaseModel):
    """Input payload for synthetic data generation."""

    volume: SyntheticVolumeConfig = Field(default_factory=SyntheticVolumeConfig)
    random_seed: int | None = None
    include_records: bool = False
    max_inline_records_per_dataset: int = Field(default=200, ge=1, le=5000)
    data_dictionary_path: str | None = None
    database_model_path: str | None = None


class SyntheticDataGenerationResponse(BaseModel):
    """Generated synthetic data output and metadata provenance."""

    dataset_id: str
    generated_at: datetime
    metadata_sources: dict[str, str]
    resolved_tables: dict[str, str | None]
    volumes: dict[str, int]
    truncated_records: dict[str, bool]
    samples: SyntheticDataPayload
    records: SyntheticDataPayload | None = None


class SyntheticDataConfigTemplateResponse(BaseModel):
    """Template response to help clients configure synthetic generation."""

    supported_entities: list[str] = Field(default_factory=list)
    default_volume: SyntheticVolumeConfig
    override_keys: list[str] = Field(default_factory=list)
    metadata_inputs: list[str] = Field(default_factory=list)
