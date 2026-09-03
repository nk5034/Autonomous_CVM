"""Unit tests for Phase 9 campaign simulation service."""
from __future__ import annotations

from src.schemas.simulation import CampaignSimulationRequest
from src.services.campaign_simulation import CampaignSimulationService


def _payload() -> CampaignSimulationRequest:
    return CampaignSimulationRequest.model_validate(
        {
            "campaign_configuration": {
                "campaign_name": "Test campaign",
                "base_population": 100000,
                "baseline_response_rate": 0.1,
                "baseline_conversion_rate": 0.2,
                "average_revenue_per_conversion": 100.0,
                "planning_horizon_days": 30,
            },
            "selection_rules": [
                {
                    "name": "Segment include",
                    "field": "segment",
                    "operator": "in",
                    "value": ["at_risk", "growth"],
                    "estimated_match_rate": 0.8,
                },
                {
                    "name": "Recent activity",
                    "field": "last_active_days",
                    "operator": "lte",
                    "value": 90,
                    "estimated_match_rate": 0.75,
                },
            ],
            "control_group": {"enabled": True, "holdout_ratio": 0.1},
            "volume_constraints": {
                "min_audience": 10000,
                "max_audience": 50000,
                "max_contacts_total": 90000,
            },
            "contact_policies": [
                {
                    "channel": "email",
                    "allocation_ratio": 0.7,
                    "max_contacts_per_customer": 2,
                    "unit_cost": 0.03,
                    "response_lift": 0.1,
                    "conversion_lift": 0.05,
                },
                {
                    "channel": "sms",
                    "allocation_ratio": 0.3,
                    "max_contacts_per_customer": 1,
                    "unit_cost": 0.08,
                    "response_lift": 0.25,
                    "conversion_lift": 0.08,
                },
            ],
        }
    )


def test_simulation_service_generates_required_forecasts() -> None:
    service = CampaignSimulationService()
    response = service.run(_payload())

    assert response.simulation_id.startswith("sim_")
    assert response.expected_audience.base_population == 100000
    assert response.expected_audience.eligible_audience == 60000
    assert response.expected_audience.control_group_size == 6000
    assert response.expected_audience.target_audience == 45000

    assert response.revenue_forecast.expected_revenue > 0
    assert response.cost_forecast.expected_cost > 0
    assert response.response_forecast.expected_responses > 0
    assert isinstance(response.roi_forecast.roi, float)

    stage_names = [stage.stage for stage in response.waterfall_analysis.stages]
    assert "Base Population" in stage_names
    assert "After Volume Constraints" in stage_names


def test_simulation_template_contains_all_input_domains() -> None:
    service = CampaignSimulationService()
    template = service.get_template()

    assert template.campaign_configuration.base_population > 0
    assert template.selection_rule_template.name
    assert template.control_group.holdout_ratio >= 0
    assert template.volume_constraints.max_audience is not None
    assert len(template.contact_policies) >= 1
