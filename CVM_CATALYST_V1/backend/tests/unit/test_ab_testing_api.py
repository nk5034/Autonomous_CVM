"""Unit tests for Phase 10 AB testing API endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


@pytest.mark.asyncio
async def test_ab_testing_endpoints(monkeypatch) -> None:
    from src.api.v1.endpoints import ab_testing as ab_testing_endpoint

    monkeypatch.setattr(
        ab_testing_endpoint.ab_testing_service,
        "get_template",
        lambda: {
            "campaign_id": 501,
            "experiment_name": "Retention Subject Line Experiment",
            "hypothesis": "Personalization improves conversion",
            "audience_size": 120000,
            "confidence_level_target": 0.95,
            "control": {
                "name": "control",
                "traffic_percentage": 0.2,
                "conversion_rate": 0.05,
            },
            "variants": [
                {
                    "name": "variant_a_personalized",
                    "traffic_percentage": 0.4,
                    "conversion_rate": 0.058,
                }
            ],
        },
    )

    monkeypatch.setattr(
        ab_testing_endpoint.ab_testing_service,
        "run",
        lambda payload: {
            "experiment_id": "ab_test_123",
            "generated_at": "2026-09-01T00:00:00+00:00",
            "campaign_id": payload.campaign_id,
            "experiment_name": payload.experiment_name,
            "hypothesis": payload.hypothesis,
            "confidence_level_target": payload.confidence_level_target,
            "arms": [
                {
                    "name": "control",
                    "is_control": True,
                    "allocation": 0.2,
                    "audience": 20000,
                    "conversion_rate": 0.05,
                    "expected_conversions": 1000,
                },
                {
                    "name": "variant_a",
                    "is_control": False,
                    "allocation": 0.8,
                    "audience": 80000,
                    "conversion_rate": 0.058,
                    "expected_conversions": 4640,
                },
            ],
            "variant_performance": [
                {
                    "name": "variant_a",
                    "lift": 0.16,
                    "absolute_lift": 0.008,
                    "z_score": 5.0,
                    "p_value": 0.000001,
                    "confidence": 0.999999,
                    "statistically_significant": True,
                    "incremental_conversions": 640,
                }
            ],
            "recommendation": {
                "action": "promote_variant",
                "rationale": "variant_a beats control at required confidence",
                "recommended_variant": "variant_a",
            },
            "dashboard": {
                "kpis": [
                    {"label": "Total Audience", "value": 100000, "format": "number"},
                ],
                "traffic_allocation": [
                    {"label": "control", "value": 0.2},
                    {"label": "variant_a", "value": 0.8},
                ],
                "conversion_rates": [
                    {"label": "control", "value": 0.05},
                    {"label": "variant_a", "value": 0.058},
                ],
                "lift_by_variant": [
                    {"label": "variant_a", "value": 0.16},
                ],
                "confidence_by_variant": [
                    {"label": "variant_a", "value": 0.999999},
                ],
            },
        },
    )

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        template_response = await client.get("/api/v1/ab-testing/template")
        assert template_response.status_code == 200
        assert template_response.json()["campaign_id"] == 501

        run_response = await client.post(
            "/api/v1/ab-testing/run",
            json={
                "campaign_id": 700,
                "experiment_name": "Welcome Offer Test",
                "hypothesis": "Urgency improves conversion",
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
                        "traffic_percentage": 0.8,
                        "conversion_rate": 0.058,
                    }
                ],
            },
        )
        assert run_response.status_code == 200
        body = run_response.json()
        assert body["experiment_id"] == "ab_test_123"
        assert body["recommendation"]["action"] == "promote_variant"