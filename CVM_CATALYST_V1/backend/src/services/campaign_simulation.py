"""Phase 9 campaign simulation engine service."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.schemas.simulation import (
    CampaignConfiguration,
    CampaignSimulationRequest,
    CampaignSimulationTemplateResponse,
    CampaignSimulationResponse,
    ChannelCostBreakdown,
    ContactPolicy,
    DashboardKPI,
    DashboardSeriesPoint,
    ExpectedAudience,
    ROIForecast,
    ResponseForecast,
    RevenueForecast,
    SelectionRule,
    SimulationDashboard,
    WaterfallAnalysis,
    WaterfallStagePoint,
    CostForecast,
)


class CampaignSimulationService:
    """Simulates campaign reach and commercial outcomes from planning inputs."""

    def get_template(self) -> CampaignSimulationTemplateResponse:
        return CampaignSimulationTemplateResponse(
            campaign_configuration=CampaignConfiguration(
                campaign_name="Retention Uplift Sprint",
                base_population=150000,
                baseline_response_rate=0.08,
                baseline_conversion_rate=0.2,
                average_revenue_per_conversion=120.0,
                planning_horizon_days=30,
            ),
            selection_rule_template=SelectionRule(
                name="Tenure at least 6 months",
                field="tenure_months",
                operator="gte",
                value=6,
                estimated_match_rate=0.85,
            ),
            control_group={"enabled": True, "holdout_ratio": 0.1},
            volume_constraints={"min_audience": 10000, "max_audience": 90000, "max_contacts_total": 180000},
            contact_policies=[
                ContactPolicy(
                    channel="email",
                    allocation_ratio=0.6,
                    max_contacts_per_customer=2,
                    unit_cost=0.03,
                    response_lift=0.12,
                    conversion_lift=0.05,
                ),
                ContactPolicy(
                    channel="sms",
                    allocation_ratio=0.4,
                    max_contacts_per_customer=1,
                    unit_cost=0.07,
                    response_lift=0.2,
                    conversion_lift=0.08,
                ),
            ],
        )

    def run(self, payload: CampaignSimulationRequest) -> CampaignSimulationResponse:
        cfg = payload.campaign_configuration
        rules = payload.selection_rules
        control = payload.control_group
        constraints = payload.volume_constraints
        contact_policies = self._normalize_policies(payload.contact_policies)

        base_count = cfg.base_population
        eligible_count = base_count

        waterfall = [
            WaterfallStagePoint(stage="Base Population", count=base_count, retention_rate=1.0),
        ]

        for rule in rules:
            eligible_count = max(0, round(eligible_count * rule.estimated_match_rate))
            waterfall.append(
                WaterfallStagePoint(
                    stage=f"Rule: {rule.name}",
                    count=eligible_count,
                    retention_rate=(eligible_count / base_count) if base_count else 0.0,
                )
            )

        control_group_size = round(eligible_count * control.holdout_ratio) if control.enabled else 0
        target_audience = max(0, eligible_count - control_group_size)
        waterfall.append(
            WaterfallStagePoint(
                stage="After Control Group",
                count=target_audience,
                retention_rate=(target_audience / base_count) if base_count else 0.0,
            )
        )

        constrained_audience = target_audience
        if constraints.max_audience is not None:
            constrained_audience = min(constrained_audience, constraints.max_audience)

        max_contacts_per_customer = max(policy.max_contacts_per_customer for policy in contact_policies)
        if constraints.max_contacts_total is not None:
            constrained_by_contacts = constraints.max_contacts_total // max_contacts_per_customer
            constrained_audience = min(constrained_audience, constrained_by_contacts)

        constrained_audience = max(constrained_audience, constraints.min_audience)
        constrained_audience = min(constrained_audience, eligible_count)

        waterfall.append(
            WaterfallStagePoint(
                stage="After Volume Constraints",
                count=constrained_audience,
                retention_rate=(constrained_audience / base_count) if base_count else 0.0,
            )
        )

        weighted_response_lift = sum(policy.allocation_ratio * policy.response_lift for policy in contact_policies)
        weighted_conversion_lift = sum(policy.allocation_ratio * policy.conversion_lift for policy in contact_policies)
        effective_response_rate = max(0.0, cfg.baseline_response_rate * (1 + weighted_response_lift))
        effective_conversion_rate = max(0.0, cfg.baseline_conversion_rate * (1 + weighted_conversion_lift))

        expected_responses = round(constrained_audience * effective_response_rate)
        expected_conversions = round(expected_responses * effective_conversion_rate)
        expected_revenue = expected_conversions * cfg.average_revenue_per_conversion

        channel_breakdown: list[ChannelCostBreakdown] = []
        total_cost = 0.0
        total_contacts = 0
        for policy in contact_policies:
            channel_audience = round(constrained_audience * policy.allocation_ratio)
            channel_contacts = channel_audience * policy.max_contacts_per_customer
            channel_response_rate = max(0.0, cfg.baseline_response_rate * (1 + policy.response_lift))
            channel_responses = round(channel_audience * channel_response_rate)
            channel_cost = channel_contacts * policy.unit_cost
            total_cost += channel_cost
            total_contacts += channel_contacts

            channel_breakdown.append(
                ChannelCostBreakdown(
                    channel=policy.channel,
                    audience=channel_audience,
                    contacts=channel_contacts,
                    cost=round(channel_cost, 2),
                    response_rate=round(channel_response_rate, 4),
                    responses=channel_responses,
                )
            )

        incremental_profit = expected_revenue - total_cost
        roi = (incremental_profit / total_cost) if total_cost > 0 else 0.0
        break_even_revenue = total_cost / cfg.average_revenue_per_conversion if cfg.average_revenue_per_conversion > 0 else 0.0
        break_even_responses = break_even_revenue / effective_conversion_rate if effective_conversion_rate > 0 else 0.0
        break_even_response_rate = (break_even_responses / constrained_audience) if constrained_audience > 0 else 0.0

        expected_audience = ExpectedAudience(
            base_population=base_count,
            eligible_audience=eligible_count,
            control_group_size=control_group_size,
            target_audience=constrained_audience,
        )

        response_forecast = ResponseForecast(
            baseline_response_rate=cfg.baseline_response_rate,
            effective_response_rate=round(effective_response_rate, 4),
            expected_responses=expected_responses,
            expected_conversions=expected_conversions,
        )

        revenue_forecast = RevenueForecast(
            expected_revenue=round(expected_revenue, 2),
            expected_conversions=expected_conversions,
            average_revenue_per_conversion=cfg.average_revenue_per_conversion,
        )

        cost_forecast = CostForecast(
            expected_cost=round(total_cost, 2),
            cost_per_contact=round((total_cost / total_contacts), 4) if total_contacts else 0.0,
            channel_breakdown=channel_breakdown,
        )

        roi_forecast = ROIForecast(
            roi=round(roi, 4),
            incremental_profit=round(incremental_profit, 2),
            break_even_response_rate=round(break_even_response_rate, 4),
        )

        dashboard = self._build_dashboard(
            expected_audience=expected_audience,
            waterfall=waterfall,
            revenue=revenue_forecast,
            cost=cost_forecast,
            response=response_forecast,
            roi=roi_forecast,
        )

        return CampaignSimulationResponse(
            simulation_id=f"sim_{uuid4().hex[:12]}",
            generated_at=datetime.now(UTC),
            expected_audience=expected_audience,
            waterfall_analysis=WaterfallAnalysis(stages=waterfall),
            revenue_forecast=revenue_forecast,
            cost_forecast=cost_forecast,
            response_forecast=response_forecast,
            roi_forecast=roi_forecast,
            dashboard=dashboard,
        )

    def _normalize_policies(self, policies: list[ContactPolicy]) -> list[ContactPolicy]:
        if not policies:
            return [
                ContactPolicy(
                    channel="email",
                    allocation_ratio=1.0,
                    max_contacts_per_customer=1,
                    unit_cost=0.03,
                    response_lift=0.0,
                    conversion_lift=0.0,
                )
            ]

        ratio_sum = sum(max(0.0, policy.allocation_ratio) for policy in policies)
        if ratio_sum <= 0:
            even_ratio = 1 / len(policies)
            return [policy.model_copy(update={"allocation_ratio": even_ratio}) for policy in policies]

        return [
            policy.model_copy(update={"allocation_ratio": policy.allocation_ratio / ratio_sum})
            for policy in policies
        ]

    def _build_dashboard(
        self,
        expected_audience: ExpectedAudience,
        waterfall: list[WaterfallStagePoint],
        revenue: RevenueForecast,
        cost: CostForecast,
        response: ResponseForecast,
        roi: ROIForecast,
    ) -> SimulationDashboard:
        kpis = [
            DashboardKPI(label="Target Audience", value=expected_audience.target_audience, format="number"),
            DashboardKPI(label="Expected Revenue", value=revenue.expected_revenue, format="currency"),
            DashboardKPI(label="Expected Cost", value=cost.expected_cost, format="currency"),
            DashboardKPI(label="ROI", value=roi.roi, format="percent"),
            DashboardKPI(label="Expected Responses", value=response.expected_responses, format="number"),
        ]

        waterfall_series = [
            DashboardSeriesPoint(label=stage.stage, value=stage.count)
            for stage in waterfall
        ]

        channel_mix = [
            DashboardSeriesPoint(label=item.channel, value=item.audience)
            for item in cost.channel_breakdown
        ]

        revenue_vs_cost = [
            DashboardSeriesPoint(label="Revenue", value=revenue.expected_revenue),
            DashboardSeriesPoint(label="Cost", value=cost.expected_cost),
            DashboardSeriesPoint(label="Profit", value=roi.incremental_profit),
        ]

        return SimulationDashboard(
            kpis=kpis,
            waterfall=waterfall_series,
            channel_mix=channel_mix,
            revenue_vs_cost=revenue_vs_cost,
        )
