# Campaign Simulation API (Phase 9)

Base path: /api/v1/campaign-simulation

Phase 9 introduces a campaign simulation engine that transforms planning inputs into audience, response, cost, revenue, and ROI forecasts.

Inputs:
- Campaign configuration
- Selection rules
- Control groups
- Volume constraints
- Contact policies

Outputs:
- Expected audience
- Waterfall analysis
- Revenue forecast
- Cost forecast
- Response forecast
- ROI forecast
- Dashboard-ready KPI and chart series data

## Get Template

GET /config/template

Returns starter values for all required input domains.

## Run Simulation

POST /run

Example request:

```json
{
  "campaign_configuration": {
    "campaign_name": "Q4 Retention Push",
    "base_population": 120000,
    "baseline_response_rate": 0.08,
    "baseline_conversion_rate": 0.2,
    "average_revenue_per_conversion": 140,
    "planning_horizon_days": 30
  },
  "selection_rules": [
    {
      "name": "High-risk churn segment",
      "field": "churn_risk_band",
      "operator": "in",
      "value": ["high", "very_high"],
      "estimated_match_rate": 0.62
    },
    {
      "name": "Digital reachable",
      "field": "email_opt_in",
      "operator": "eq",
      "value": "true",
      "estimated_match_rate": 0.81
    }
  ],
  "control_group": {
    "enabled": true,
    "holdout_ratio": 0.1
  },
  "volume_constraints": {
    "min_audience": 10000,
    "max_audience": 50000,
    "max_contacts_total": 120000
  },
  "contact_policies": [
    {
      "channel": "email",
      "allocation_ratio": 0.7,
      "max_contacts_per_customer": 2,
      "unit_cost": 0.03,
      "response_lift": 0.1,
      "conversion_lift": 0.05
    },
    {
      "channel": "sms",
      "allocation_ratio": 0.3,
      "max_contacts_per_customer": 1,
      "unit_cost": 0.08,
      "response_lift": 0.25,
      "conversion_lift": 0.08
    }
  ]
}
```

Example response shape:

```json
{
  "simulation_id": "sim_6f8ac67d2da8",
  "generated_at": "2026-09-01T12:15:00+00:00",
  "expected_audience": {
    "base_population": 120000,
    "eligible_audience": 60264,
    "control_group_size": 6026,
    "target_audience": 50000
  },
  "waterfall_analysis": {
    "stages": [
      { "stage": "Base Population", "count": 120000, "retention_rate": 1.0 },
      { "stage": "Rule: High-risk churn segment", "count": 74400, "retention_rate": 0.62 },
      { "stage": "Rule: Digital reachable", "count": 60264, "retention_rate": 0.5022 },
      { "stage": "After Control Group", "count": 54238, "retention_rate": 0.452 },
      { "stage": "After Volume Constraints", "count": 50000, "retention_rate": 0.4167 }
    ]
  },
  "revenue_forecast": {
    "expected_revenue": 915600,
    "expected_conversions": 6540,
    "average_revenue_per_conversion": 140
  },
  "cost_forecast": {
    "expected_cost": 5700,
    "cost_per_contact": 0.05,
    "channel_breakdown": []
  },
  "response_forecast": {
    "baseline_response_rate": 0.08,
    "effective_response_rate": 0.0908,
    "expected_responses": 4540,
    "expected_conversions": 944
  },
  "roi_forecast": {
    "roi": 159.6316,
    "incremental_profit": 909900,
    "break_even_response_rate": 0.0006
  },
  "dashboard": {
    "kpis": [],
    "waterfall": [],
    "channel_mix": [],
    "revenue_vs_cost": []
  }
}
```
