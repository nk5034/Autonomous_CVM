"""Unit tests for Phase 9 campaign simulation API endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


@pytest.mark.asyncio
async def test_campaign_simulation_endpoints(monkeypatch) -> None:
    from src.api.v1.endpoints import campaign_simulation as simulation_endpoint

    monkeypatch.setattr(
        simulation_endpoint.simulation_service,
        "get_template",
        lambda: {
            "campaign_configuration": {
                "campaign_name": "Retention Uplift Sprint",
                "base_population": 150000,
                "baseline_response_rate": 0.08,
                "baseline_conversion_rate": 0.2,
                "average_revenue_per_conversion": 120.0,
                "planning_horizon_days": 30,
            },
            "selection_rule_template": {
                "name": "Tenure at least 6 months",
                "field": "tenure_months",
                "operator": "gte",
                "value": 6,
                "estimated_match_rate": 0.85,
            },
            "control_group": {"enabled": True, "holdout_ratio": 0.1},
            "volume_constraints": {
                "min_audience": 10000,
                "max_audience": 90000,
                "max_contacts_total": 180000,
            },
            "contact_policies": [
                {
                    "channel": "email",
                    "allocation_ratio": 0.6,
                    "max_contacts_per_customer": 2,
                    "unit_cost": 0.03,
                    "response_lift": 0.12,
                    "conversion_lift": 0.05,
                }
            ],
        },
    )

    monkeypatch.setattr(
        simulation_endpoint.simulation_service,
        "run",
        lambda payload: {
            "simulation_id": "sim_test_123",
            "generated_at": "2026-09-01T00:00:00+00:00",
            "expected_audience": {
                "base_population": 100000,
                "eligible_audience": 70000,
                "control_group_size": 7000,
                "target_audience": 50000,
            },
            "waterfall_analysis": {
                "stages": [
                    {"stage": "Base Population", "count": 100000, "retention_rate": 1.0},
                    {"stage": "After Volume Constraints", "count": 50000, "retention_rate": 0.5},
                ]
            },
            "revenue_forecast": {
                "expected_revenue": 420000.0,
                "expected_conversions": 3500,
                "average_revenue_per_conversion": 120.0,
            },
            "cost_forecast": {
                "expected_cost": 6500.0,
                "cost_per_contact": 0.05,
                "channel_breakdown": [
                    {
                        "channel": "email",
                        "audience": 30000,
                        "contacts": 60000,
                        "cost": 1800.0,
                        "response_rate": 0.09,
                        "responses": 2700,
                    }
                ],
            },
            "response_forecast": {
                "baseline_response_rate": 0.08,
                "effective_response_rate": 0.1,
                "expected_responses": 5000,
                "expected_conversions": 3500,
            },
            "roi_forecast": {
                "roi": 63.6154,
                "incremental_profit": 413500.0,
                "break_even_response_rate": 0.0015,
            },
            "dashboard": {
                "kpis": [
                    {"label": "Target Audience", "value": 50000, "format": "number"},
                    {"label": "Expected Revenue", "value": 420000.0, "format": "currency"},
                ],
                "waterfall": [
                    {"label": "Base Population", "value": 100000},
                    {"label": "After Volume Constraints", "value": 50000},
                ],
                "channel_mix": [
                    {"label": "email", "value": 30000}
                ],
                "revenue_vs_cost": [
                    {"label": "Revenue", "value": 420000.0},
                    {"label": "Cost", "value": 6500.0},
                ],
            },
        },
    )

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        template_response = await client.get("/api/v1/campaign-simulation/config/template")
        assert template_response.status_code == 200
        assert template_response.json()["campaign_configuration"]["base_population"] == 150000

        run_response = await client.post(
            "/api/v1/campaign-simulation/run",
            json={
                "campaign_configuration": {
                    "campaign_name": "Q4 Save",
                    "base_population": 100000,
                    "baseline_response_rate": 0.1,
                    "baseline_conversion_rate": 0.2,
                    "average_revenue_per_conversion": 120,
                    "planning_horizon_days": 30,
                },
                "selection_rules": [],
                "control_group": {"enabled": True, "holdout_ratio": 0.1},
                "volume_constraints": {"min_audience": 0, "max_audience": 80000, "max_contacts_total": 120000},
                "contact_policies": [
                    {
                        "channel": "email",
                        "allocation_ratio": 1,
                        "max_contacts_per_customer": 1,
                        "unit_cost": 0.03,
                        "response_lift": 0.1,
                        "conversion_lift": 0.05,
                    }
                ],
            },
        )
        assert run_response.status_code == 200
        body = run_response.json()
        assert body["simulation_id"] == "sim_test_123"
        assert body["expected_audience"]["target_audience"] == 50000
        assert "roi_forecast" in body
