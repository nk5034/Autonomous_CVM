"""Unit tests for Phase 10 AB testing service."""
from __future__ import annotations

from src.schemas.ab_testing import ABTestingRequest
from src.services.ab_testing import ABTestingService


def _payload() -> ABTestingRequest:
    return ABTestingRequest.model_validate(
        {
            "campaign_id": 700,
            "experiment_name": "Welcome Offer Test",
            "hypothesis": "Urgency-led CTA increases conversion.",
            "audience_size": 100000,
            "confidence_level_target": 0.95,
            "control": {
                "name": "control",
                "traffic_percentage": 0.2,
                "conversion_rate": 0.05,
            },
            "variants": [
                {
                    "name": "variant_a",
                    "traffic_percentage": 0.4,
                    "conversion_rate": 0.057,
                },
                {
                    "name": "variant_b",
                    "traffic_percentage": 0.4,
                    "conversion_rate": 0.062,
                },
            ],
        }
    )


def test_ab_testing_service_computes_lift_confidence_and_recommendation() -> None:
    service = ABTestingService()
    response = service.run(_payload())

    assert response.experiment_id.startswith("ab_")
    assert response.campaign_id == 700
    assert len(response.arms) == 3

    allocations = sum(arm.allocation for arm in response.arms)
    assert abs(allocations - 1.0) < 1e-4

    control = next(arm for arm in response.arms if arm.is_control)
    assert control.name == "control"

    assert len(response.variant_performance) == 2
    best = max(response.variant_performance, key=lambda item: item.lift)
    assert best.lift > 0
    assert 0 <= best.confidence <= 1
    assert response.recommendation.action in {"promote_variant", "collect_more_data", "keep_control"}


def test_ab_testing_template_contains_control_and_variants() -> None:
    service = ABTestingService()
    template = service.get_template()

    assert template.campaign_id > 0
    assert template.control.traffic_percentage > 0
    assert len(template.variants) >= 1