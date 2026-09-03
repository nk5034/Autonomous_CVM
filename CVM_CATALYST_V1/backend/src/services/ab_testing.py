"""Phase 10 A/B testing framework service."""
from __future__ import annotations

import math
from datetime import UTC, datetime
from uuid import uuid4

from src.schemas.ab_testing import (
    ABTestingDashboard,
    ABTestingRequest,
    ABTestingResponse,
    ABTestingTemplateResponse,
    DashboardKPI,
    DashboardSeriesPoint,
    ExperimentArm,
    Recommendation,
    VariantPerformance,
    VariantConfig,
)


class ABTestingService:
    """Builds and evaluates A/B test plans for campaign optimization."""

    def get_template(self) -> ABTestingTemplateResponse:
        return ABTestingTemplateResponse(
            campaign_id=501,
            experiment_name="Retention Subject Line Experiment",
            hypothesis="Personalized subject lines increase conversion over control.",
            audience_size=120000,
            confidence_level_target=0.95,
            control={
                "name": "control",
                "traffic_percentage": 0.2,
                "conversion_rate": 0.05,
            },
            variants=[
                VariantConfig(
                    name="variant_a_personalized",
                    traffic_percentage=0.4,
                    conversion_rate=0.058,
                    description="Adds customer first-name in subject line.",
                ),
                VariantConfig(
                    name="variant_b_urgency",
                    traffic_percentage=0.4,
                    conversion_rate=0.061,
                    description="Uses urgency-led copy and deadline framing.",
                ),
            ],
        )

    def run(self, payload: ABTestingRequest) -> ABTestingResponse:
        allocations = self._normalize_allocations(payload)
        arms = self._build_arms(payload, allocations)
        control_arm = next(arm for arm in arms if arm.is_control)

        performance: list[VariantPerformance] = []
        for arm in arms:
            if arm.is_control:
                continue

            confidence, p_value, z_score = self._confidence_two_proportion(
                control_successes=control_arm.expected_conversions,
                control_trials=control_arm.audience,
                variant_successes=arm.expected_conversions,
                variant_trials=arm.audience,
            )
            absolute_lift = arm.conversion_rate - control_arm.conversion_rate
            relative_lift = (
                (absolute_lift / control_arm.conversion_rate) if control_arm.conversion_rate > 0 else 0.0
            )
            incremental = arm.expected_conversions - round(arm.audience * control_arm.conversion_rate)

            performance.append(
                VariantPerformance(
                    name=arm.name,
                    lift=round(relative_lift, 6),
                    absolute_lift=round(absolute_lift, 6),
                    z_score=round(z_score, 6),
                    p_value=round(p_value, 8),
                    confidence=round(confidence, 6),
                    statistically_significant=confidence >= payload.confidence_level_target,
                    incremental_conversions=incremental,
                )
            )

        recommendation = self._build_recommendation(payload.confidence_level_target, performance)
        dashboard = self._build_dashboard(arms, performance)

        return ABTestingResponse(
            experiment_id=f"ab_{uuid4().hex[:12]}",
            generated_at=datetime.now(UTC),
            campaign_id=payload.campaign_id,
            experiment_name=payload.experiment_name,
            hypothesis=payload.hypothesis,
            confidence_level_target=payload.confidence_level_target,
            arms=arms,
            variant_performance=performance,
            recommendation=recommendation,
            dashboard=dashboard,
        )

    def _normalize_allocations(self, payload: ABTestingRequest) -> dict[str, float]:
        raw_allocations = {payload.control.name: payload.control.traffic_percentage}
        raw_allocations.update({variant.name: variant.traffic_percentage for variant in payload.variants})

        total = sum(max(0.0, allocation) for allocation in raw_allocations.values())
        if total <= 0:
            even = 1 / len(raw_allocations)
            return {name: even for name in raw_allocations}

        return {name: allocation / total for name, allocation in raw_allocations.items()}

    def _build_arms(self, payload: ABTestingRequest, allocations: dict[str, float]) -> list[ExperimentArm]:
        control_allocation = allocations[payload.control.name]
        control_audience = round(payload.audience_size * control_allocation)
        control_conversions = round(control_audience * payload.control.conversion_rate)

        arms: list[ExperimentArm] = [
            ExperimentArm(
                name=payload.control.name,
                is_control=True,
                allocation=round(control_allocation, 6),
                audience=control_audience,
                conversion_rate=payload.control.conversion_rate,
                expected_conversions=control_conversions,
            )
        ]

        for variant in payload.variants:
            allocation = allocations[variant.name]
            audience = round(payload.audience_size * allocation)
            conversions = round(audience * variant.conversion_rate)
            arms.append(
                ExperimentArm(
                    name=variant.name,
                    is_control=False,
                    allocation=round(allocation, 6),
                    audience=audience,
                    conversion_rate=variant.conversion_rate,
                    expected_conversions=conversions,
                )
            )

        return arms

    def _confidence_two_proportion(
        self,
        control_successes: int,
        control_trials: int,
        variant_successes: int,
        variant_trials: int,
    ) -> tuple[float, float, float]:
        if control_trials <= 0 or variant_trials <= 0:
            return 0.0, 1.0, 0.0

        p1 = control_successes / control_trials
        p2 = variant_successes / variant_trials
        pooled = (control_successes + variant_successes) / (control_trials + variant_trials)
        se = math.sqrt(max(0.0, pooled * (1 - pooled) * ((1 / control_trials) + (1 / variant_trials))))

        if se == 0:
            return 0.0, 1.0, 0.0

        z_score = (p2 - p1) / se
        # Two-tailed p-value using the normal distribution CDF.
        p_value = math.erfc(abs(z_score) / math.sqrt(2))
        confidence = max(0.0, min(1.0, 1 - p_value))
        return confidence, p_value, z_score

    def _build_recommendation(
        self,
        confidence_target: float,
        performance: list[VariantPerformance],
    ) -> Recommendation:
        significant_positive = [
            item
            for item in performance
            if item.statistically_significant and item.incremental_conversions > 0 and item.lift > 0
        ]

        if significant_positive:
            winner = max(
                significant_positive,
                key=lambda item: (item.incremental_conversions, item.lift, item.confidence),
            )
            return Recommendation(
                action="promote_variant",
                recommended_variant=winner.name,
                rationale=(
                    f"{winner.name} exceeds confidence target ({confidence_target:.2%}) "
                    f"with positive lift and highest incremental conversions."
                ),
            )

        near_confident = [item for item in performance if item.confidence >= max(0.8, confidence_target - 0.1)]
        if near_confident:
            candidate = max(near_confident, key=lambda item: (item.lift, item.incremental_conversions))
            return Recommendation(
                action="collect_more_data",
                recommended_variant=candidate.name,
                rationale=(
                    f"{candidate.name} shows promising lift but has not met the required "
                    f"confidence threshold of {confidence_target:.2%}."
                ),
            )

        return Recommendation(
            action="keep_control",
            recommended_variant=None,
            rationale="No variant demonstrates reliable positive lift. Keep control and iterate on creatives.",
        )

    def _build_dashboard(
        self,
        arms: list[ExperimentArm],
        performance: list[VariantPerformance],
    ) -> ABTestingDashboard:
        best_lift = max((item.lift for item in performance), default=0.0)
        best_confidence = max((item.confidence for item in performance), default=0.0)

        kpis = [
            DashboardKPI(label="Total Audience", value=sum(arm.audience for arm in arms), format="number"),
            DashboardKPI(label="Control Conversion Rate", value=arms[0].conversion_rate, format="percent"),
            DashboardKPI(label="Best Relative Lift", value=best_lift, format="percent"),
            DashboardKPI(label="Best Statistical Confidence", value=best_confidence, format="percent"),
        ]

        traffic_allocation = [
            DashboardSeriesPoint(label=arm.name, value=arm.allocation)
            for arm in arms
        ]
        conversion_rates = [
            DashboardSeriesPoint(label=arm.name, value=arm.conversion_rate)
            for arm in arms
        ]
        lift_by_variant = [
            DashboardSeriesPoint(label=item.name, value=item.lift)
            for item in performance
        ]
        confidence_by_variant = [
            DashboardSeriesPoint(label=item.name, value=item.confidence)
            for item in performance
        ]

        return ABTestingDashboard(
            kpis=kpis,
            traffic_allocation=traffic_allocation,
            conversion_rates=conversion_rates,
            lift_by_variant=lift_by_variant,
            confidence_by_variant=confidence_by_variant,
        )