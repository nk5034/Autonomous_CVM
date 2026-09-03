"""Schemas for Phase 10 A/B testing APIs."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ControlGroupConfig(BaseModel):
    """Configuration for the control cohort."""

    name: str = "control"
    traffic_percentage: float = Field(default=0.2, gt=0.0, le=1.0)
    conversion_rate: float = Field(default=0.05, ge=0.0, le=1.0)


class VariantConfig(BaseModel):
    """Configuration and assumptions for a treatment variant."""

    name: str
    traffic_percentage: float = Field(gt=0.0, le=1.0)
    conversion_rate: float = Field(ge=0.0, le=1.0)
    description: str | None = None


class ABTestingRequest(BaseModel):
    """Input for creating and analyzing an A/B test plan."""

    campaign_id: int = Field(ge=1)
    experiment_name: str
    hypothesis: str
    audience_size: int = Field(default=100000, ge=100)
    confidence_level_target: float = Field(default=0.95, ge=0.8, le=0.999)
    control: ControlGroupConfig = Field(default_factory=ControlGroupConfig)
    variants: list[VariantConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_variants(self) -> ABTestingRequest:
        if not self.variants:
            raise ValueError("At least one treatment variant is required.")

        names = [self.control.name, *[variant.name for variant in self.variants]]
        lowered = [name.lower() for name in names]
        if len(set(lowered)) != len(lowered):
            raise ValueError("Control and variant names must be unique.")

        return self


class ExperimentArm(BaseModel):
    name: str
    is_control: bool
    allocation: float
    audience: int
    conversion_rate: float
    expected_conversions: int


class VariantPerformance(BaseModel):
    name: str
    lift: float
    absolute_lift: float
    z_score: float
    p_value: float
    confidence: float
    statistically_significant: bool
    incremental_conversions: int


class Recommendation(BaseModel):
    action: str
    rationale: str
    recommended_variant: str | None = None


class DashboardKPI(BaseModel):
    label: str
    value: float
    format: str = "number"


class DashboardSeriesPoint(BaseModel):
    label: str
    value: float


class ABTestingDashboard(BaseModel):
    kpis: list[DashboardKPI] = Field(default_factory=list)
    traffic_allocation: list[DashboardSeriesPoint] = Field(default_factory=list)
    conversion_rates: list[DashboardSeriesPoint] = Field(default_factory=list)
    lift_by_variant: list[DashboardSeriesPoint] = Field(default_factory=list)
    confidence_by_variant: list[DashboardSeriesPoint] = Field(default_factory=list)


class ABTestingResponse(BaseModel):
    experiment_id: str
    generated_at: datetime
    campaign_id: int
    experiment_name: str
    hypothesis: str
    confidence_level_target: float
    arms: list[ExperimentArm]
    variant_performance: list[VariantPerformance]
    recommendation: Recommendation
    dashboard: ABTestingDashboard


class ABTestingTemplateResponse(BaseModel):
    campaign_id: int
    experiment_name: str
    hypothesis: str
    audience_size: int
    confidence_level_target: float
    control: ControlGroupConfig
    variants: list[VariantConfig]