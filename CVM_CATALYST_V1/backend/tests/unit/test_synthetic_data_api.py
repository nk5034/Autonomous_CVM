"""Unit tests for Phase 8 synthetic data API endpoints."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _load_synthetic_endpoint_module():
    module_name = "phase8_test_synthetic_endpoint"
    if module_name in sys.modules:
        return sys.modules[module_name]

    module_path = Path(__file__).resolve().parents[2] / "src" / "api" / "v1" / "endpoints" / "synthetic_data.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load synthetic_data endpoint module for testing.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_synthetic_data_endpoints(monkeypatch) -> None:
    synthetic_endpoint = _load_synthetic_endpoint_module()

    app = FastAPI()
    app.include_router(synthetic_endpoint.router, prefix="/api/v1")

    monkeypatch.setattr(
        synthetic_endpoint.synthetic_data_service,
        "get_generation_template",
        lambda: {
            "supported_entities": [
                "customer_data",
                "subscription_data",
                "household_data",
                "revenue_data",
                "interaction_history",
                "scores",
                "channel_responses",
            ],
            "default_volume": {
                "customer_count": 1000,
                "household_coverage_ratio": 0.45,
                "avg_subscriptions_per_customer": 1.2,
                "avg_interactions_per_customer": 6,
                "channel_response_rate": 0.28,
                "conversion_rate": 0.08,
                "record_overrides": {},
            },
            "override_keys": [
                "customer_data",
                "subscription_data",
                "household_data",
                "revenue_data",
                "interaction_history",
                "scores",
                "channel_responses",
            ],
            "metadata_inputs": ["data_dictionary_path", "database_model_path"],
        },
    )

    monkeypatch.setattr(
        synthetic_endpoint.synthetic_data_service,
        "generate_dataset",
        lambda **kwargs: {
            "dataset_id": "syn_test_123",
            "generated_at": "2026-09-01T00:00:00+00:00",
            "metadata_sources": {
                "data_dictionary": "knowledge/Data Dictionary.xlsx",
                "database_model": "knowledge/Database Model.xlsx",
            },
            "resolved_tables": {
                "customer_data": "customer",
                "subscription_data": "subscription",
                "household_data": "household",
                "revenue_data": "revenue",
                "interaction_history": "interaction_history",
                "scores": "customer_scores",
                "channel_responses": "channel_responses",
            },
            "volumes": {
                "customer_data": 100,
                "subscription_data": 120,
                "household_data": 45,
                "revenue_data": 120,
                "interaction_history": 600,
                "scores": 100,
                "channel_responses": 168,
            },
            "truncated_records": {
                "customer_data": False,
                "subscription_data": False,
                "household_data": False,
                "revenue_data": False,
                "interaction_history": False,
                "scores": False,
                "channel_responses": False,
            },
            "samples": {
                "customer_data": [{"customer_id": "C0000001"}],
                "subscription_data": [{"subscription_id": "S0000001"}],
                "household_data": [{"household_id": "H0000001"}],
                "revenue_data": [{"revenue_id": "REV00000001"}],
                "interaction_history": [{"interaction_id": "I00000001"}],
                "scores": [{"score_id": "SC00000001"}],
                "channel_responses": [{"response_id": "R00000001"}],
            },
            "records": None,
        },
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        template_response = await client.get("/api/v1/synthetic-data/config/template")
        assert template_response.status_code == 200
        assert "customer_data" in template_response.json()["supported_entities"]

        generate_response = await client.post(
            "/api/v1/synthetic-data/generate",
            json={
                "volume": {
                    "customer_count": 100,
                    "household_coverage_ratio": 0.45,
                    "avg_subscriptions_per_customer": 1.2,
                    "avg_interactions_per_customer": 6,
                    "channel_response_rate": 0.28,
                    "conversion_rate": 0.08,
                    "record_overrides": {},
                },
                "random_seed": 7,
                "include_records": False,
                "max_inline_records_per_dataset": 200,
            },
        )
        assert generate_response.status_code == 200
        payload = generate_response.json()
        assert payload["dataset_id"] == "syn_test_123"
        assert payload["volumes"]["customer_data"] == 100
