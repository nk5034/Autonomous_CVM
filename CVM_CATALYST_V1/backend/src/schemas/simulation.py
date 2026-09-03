"""Schemas for Phase 9 campaign simulation APIs."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RuleOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "between"]


class CampaignConfiguration(BaseModel):
    """Campaign-level assumptions used to drive forecasting."""

    campaign_name: str
    base_population: int = Field(ge=1)
    baseline_response_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    baseline_conversion_rate: float = Field(default=0.2, ge=0.0, le=1.0)
    average_revenue_per_conversion: float = Field(default=120.0, ge=0.0)
    planning_horizon_days: int = Field(default=30, ge=1)


class SelectionRule(BaseModel):
    """Rule that reduces or filters candidate audience."""

    name: str
    field: str
    operator: RuleOperator
    value: str | int | float | list[str] | list[int] | list[float]
    estimated_match_rate: float = Field(default=0.9, ge=0.0, le=1.0)


class ControlGroupConfig(BaseModel):
    """Control group (holdout) definition."""

    enabled: bool = True
    holdout_ratio: float = Field(default=0.1, ge=0.0, le=0.5)


class VolumeConstraints(BaseModel):
    """Volume and contact limits for execution feasibility."""

    min_audience: int = Field(default=0, ge=0)
    max_audience: int | None = Field(default=None, ge=1)
    max_contacts_total: int | None = Field(default=None, ge=1)


class ContactPolicy(BaseModel):
    """Channel-level contact policy and economics."""

    channel: str
    allocation_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    max_contacts_per_customer: int = Field(default=1, ge=1)
    unit_cost: float = Field(default=0.05, ge=0.0)
    response_lift: float = Field(default=0.0, ge=-1.0)
    conversion_lift: float = Field(default=0.0, ge=-1.0)


class CampaignSimulationRequest(BaseModel):
    """Input payload for simulation run."""

    campaign_configuration: CampaignConfiguration
    selection_rules: list[SelectionRule] = Field(default_factory=list)
    control_group: ControlGroupConfig = Field(default_factory=ControlGroupConfig)
    volume_constraints: VolumeConstraints = Field(default_factory=VolumeConstraints)
    contact_policies: list[ContactPolicy] = Field(default_factory=list)


class ExpectedAudience(BaseModel):
    base_population: int
    eligible_audience: int
    control_group_size: int
    target_audience: int


class WaterfallStagePoint(BaseModel):
    stage: str
    count: int
    retention_rate: float


class WaterfallAnalysis(BaseModel):
    stages: list[WaterfallStagePoint] = Field(default_factory=list)


class RevenueForecast(BaseModel):
    expected_revenue: float
    expected_conversions: int
    average_revenue_per_conversion: float


class ChannelCostBreakdown(BaseModel):
    channel: str
    audience: int
    contacts: int
    cost: float
    response_rate: float
    responses: int


class CostForecast(BaseModel):
    expected_cost: float
    cost_per_contact: float
    channel_breakdown: list[ChannelCostBreakdown] = Field(default_factory=list)


class ResponseForecast(BaseModel):
    baseline_response_rate: float
    effective_response_rate: float
    expected_responses: int
    expected_conversions: int


class ROIForecast(BaseModel):
    roi: float
    incremental_profit: float
    break_even_response_rate: float


class DashboardKPI(BaseModel):
    label: str
    value: float
    format: Literal["number", "currency", "percent"] = "number"


class DashboardSeriesPoint(BaseModel):
    label: str
    value: float


class SimulationDashboard(BaseModel):
    kpis: list[DashboardKPI] = Field(default_factory=list)
    waterfall: list[DashboardSeriesPoint] = Field(default_factory=list)
    channel_mix: list[DashboardSeriesPoint] = Field(default_factory=list)
    revenue_vs_cost: list[DashboardSeriesPoint] = Field(default_factory=list)


class CampaignSimulationResponse(BaseModel):
    simulation_id: str
    generated_at: datetime
    expected_audience: ExpectedAudience
    waterfall_analysis: WaterfallAnalysis
    revenue_forecast: RevenueForecast
    cost_forecast: CostForecast
    response_forecast: ResponseForecast
    roi_forecast: ROIForecast
    dashboard: SimulationDashboard


class CampaignSimulationTemplateResponse(BaseModel):
    campaign_configuration: CampaignConfiguration
    selection_rule_template: SelectionRule
    control_group: ControlGroupConfig
    volume_constraints: VolumeConstraints
    contact_policies: list[ContactPolicy]
