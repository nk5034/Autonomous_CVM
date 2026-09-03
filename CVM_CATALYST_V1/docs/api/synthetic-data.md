# Synthetic Data API (Phase 8)

Base path: /api/v1/synthetic-data

Phase 8 introduces metadata-driven synthetic data generation using:
- Data Dictionary workbook
- Database Model workbook

Generated domains:
- customer_data
- subscription_data
- household_data
- revenue_data
- interaction_history
- scores
- channel_responses

## Get Configuration Template

GET /config/template

Returns supported entities, default volume configuration, override keys, and metadata input fields.

Example response:

```json
{
  "supported_entities": [
    "customer_data",
    "subscription_data",
    "household_data",
    "revenue_data",
    "interaction_history",
    "scores",
    "channel_responses"
  ],
  "default_volume": {
    "customer_count": 1000,
    "household_coverage_ratio": 0.45,
    "avg_subscriptions_per_customer": 1.2,
    "avg_interactions_per_customer": 6,
    "channel_response_rate": 0.28,
    "conversion_rate": 0.08,
    "record_overrides": {}
  },
  "override_keys": [
    "customer_data",
    "subscription_data",
    "household_data",
    "revenue_data",
    "interaction_history",
    "scores",
    "channel_responses"
  ],
  "metadata_inputs": ["data_dictionary_path", "database_model_path"]
}
```

## Generate Synthetic Dataset

POST /generate

Request body:

```json
{
  "volume": {
    "customer_count": 5000,
    "household_coverage_ratio": 0.42,
    "avg_subscriptions_per_customer": 1.35,
    "avg_interactions_per_customer": 7,
    "channel_response_rate": 0.3,
    "conversion_rate": 0.09,
    "record_overrides": {
      "channel_responses": 9500
    }
  },
  "random_seed": 101,
  "include_records": false,
  "max_inline_records_per_dataset": 200,
  "data_dictionary_path": "knowledge/Data Dictionary.xlsx",
  "database_model_path": "knowledge/Database Model.xlsx"
}
```

Key notes:
- random_seed supports reproducible generation.
- include_records=false returns only samples and volume metrics.
- include_records=true includes records up to max_inline_records_per_dataset per domain.
- truncated_records indicates whether a domain was clipped in the response payload.

Example response shape:

```json
{
  "dataset_id": "syn_94e67d2f7a1c",
  "generated_at": "2026-09-01T12:00:00+00:00",
  "metadata_sources": {
    "data_dictionary": "knowledge/Data Dictionary.xlsx",
    "database_model": "knowledge/Database Model.xlsx"
  },
  "resolved_tables": {
    "customer_data": "customer",
    "subscription_data": "subscription",
    "household_data": "household",
    "revenue_data": "revenue",
    "interaction_history": "interaction_history",
    "scores": "customer_scores",
    "channel_responses": "channel_responses"
  },
  "volumes": {
    "customer_data": 5000,
    "subscription_data": 6750,
    "household_data": 2100,
    "revenue_data": 6750,
    "interaction_history": 35000,
    "scores": 5000,
    "channel_responses": 9500
  },
  "truncated_records": {
    "customer_data": false,
    "subscription_data": false,
    "household_data": false,
    "revenue_data": false,
    "interaction_history": false,
    "scores": false,
    "channel_responses": false
  },
  "samples": {
    "customer_data": [{"customer_id": "C0000001"}],
    "subscription_data": [{"subscription_id": "S0000001"}],
    "household_data": [{"household_id": "H0000001"}],
    "revenue_data": [{"revenue_id": "REV00000001"}],
    "interaction_history": [{"interaction_id": "I00000001"}],
    "scores": [{"score_id": "SC00000001"}],
    "channel_responses": [{"response_id": "R00000001"}]
  },
  "records": null
}
```
