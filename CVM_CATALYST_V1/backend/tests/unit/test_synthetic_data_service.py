"""Unit tests for Phase 8 synthetic data service."""
from __future__ import annotations

from src.schemas.synthetic import SyntheticVolumeConfig
from src.services.synthetic_data import SyntheticDataService


def _mock_metadata(source: str) -> dict:
    return {
        "source": source,
        "file_path": f"{source}.xlsx",
        "table_count": 7,
        "column_count": 14,
        "tables": [
            {
                "name": "customer",
                "columns": [
                    {"name": "customer_id", "data_type": "string"},
                    {"name": "email", "data_type": "string"},
                    {"name": "segment", "data_type": "string"},
                    {"name": "household_id", "data_type": "string"},
                ],
            },
            {
                "name": "subscription",
                "columns": [
                    {"name": "subscription_id", "data_type": "string"},
                    {"name": "customer_id", "data_type": "string"},
                    {"name": "monthly_fee", "data_type": "float"},
                ],
            },
            {
                "name": "household",
                "columns": [
                    {"name": "household_id", "data_type": "string"},
                    {"name": "income_band", "data_type": "string"},
                ],
            },
            {
                "name": "revenue",
                "columns": [
                    {"name": "revenue_id", "data_type": "string"},
                    {"name": "customer_id", "data_type": "string"},
                    {"name": "amount", "data_type": "float"},
                ],
            },
            {
                "name": "interaction_history",
                "columns": [
                    {"name": "interaction_id", "data_type": "string"},
                    {"name": "customer_id", "data_type": "string"},
                    {"name": "channel", "data_type": "string"},
                ],
            },
            {
                "name": "customer_scores",
                "columns": [
                    {"name": "score_id", "data_type": "string"},
                    {"name": "customer_id", "data_type": "string"},
                    {"name": "churn_risk_score", "data_type": "float"},
                ],
            },
            {
                "name": "channel_responses",
                "columns": [
                    {"name": "response_id", "data_type": "string"},
                    {"name": "interaction_id", "data_type": "string"},
                    {"name": "conversion", "data_type": "boolean"},
                ],
            },
        ],
    }


def test_generate_dataset_with_configurable_volume(monkeypatch) -> None:
    service = SyntheticDataService()

    monkeypatch.setattr(service.metadata_service, "parse_data_dictionary", lambda file_path=None: _mock_metadata("dd"))
    monkeypatch.setattr(service.metadata_service, "parse_database_model", lambda file_path=None: _mock_metadata("db"))

    volume = SyntheticVolumeConfig(
        customer_count=60,
        household_coverage_ratio=0.4,
        avg_subscriptions_per_customer=1.5,
        avg_interactions_per_customer=3,
        channel_response_rate=0.25,
        conversion_rate=0.1,
    )

    generated = service.generate_dataset(
        volume=volume,
        random_seed=123,
        include_records=True,
        max_inline_records_per_dataset=2000,
    )

    assert generated["volumes"]["customer_data"] == 60
    assert generated["volumes"]["household_data"] == 24
    assert generated["volumes"]["subscription_data"] == 90
    assert generated["volumes"]["interaction_history"] == 180
    assert generated["volumes"]["channel_responses"] == 45
    assert generated["volumes"]["scores"] == 60
    assert generated["volumes"]["revenue_data"] == 90

    assert generated["records"] is not None
    first_customer = generated["records"]["customer_data"][0]
    assert "customer_id" in first_customer
    assert "email" in first_customer
    assert first_customer["customer_id"].startswith("C")


def test_generate_dataset_with_overrides(monkeypatch) -> None:
    service = SyntheticDataService()

    monkeypatch.setattr(service.metadata_service, "parse_data_dictionary", lambda file_path=None: _mock_metadata("dd"))
    monkeypatch.setattr(service.metadata_service, "parse_database_model", lambda file_path=None: _mock_metadata("db"))

    volume = SyntheticVolumeConfig(
        customer_count=50,
        avg_subscriptions_per_customer=1.0,
        avg_interactions_per_customer=2,
        channel_response_rate=0.2,
        record_overrides={
            "subscription_data": 10,
            "interaction_history": 11,
            "channel_responses": 4,
            "revenue_data": 7,
        },
    )

    generated = service.generate_dataset(volume=volume, random_seed=11)

    assert generated["volumes"]["customer_data"] == 50
    assert generated["volumes"]["subscription_data"] == 10
    assert generated["volumes"]["interaction_history"] == 11
    assert generated["volumes"]["channel_responses"] == 4
    assert generated["volumes"]["revenue_data"] == 7
    assert all(value is not None for value in generated["resolved_tables"].values())
