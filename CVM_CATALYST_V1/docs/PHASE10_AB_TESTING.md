# Phase 10: A/B Testing Framework

## Overview

Phase 10 introduces a complete A/B testing framework supporting experimental design, statistical analysis, and recommendation-driven optimization.

## Features

### Control Group Management
- Named control cohort with independent traffic allocation
- Baseline conversion rate specification
- Automatic audience sizing based on total budget and allocation ratio

### Variant Creation & Traffic Allocation
- Multiple treatment variant support (1+ variants)
- Per-variant traffic percentage and expected conversion rate
- Automatic normalization of allocations to 100%
- Expected conversion calculation per arm

### Statistical Confidence
- Two-proportion z-test implementation
- Automatic p-value and confidence score calculation
- Configurable target confidence level (80%–99.9%)
- Significance determination based on threshold

### Lift Analysis
- Relative lift (% change vs control)
- Absolute lift (percentage point change)
- Z-score and p-value per variant
- Incremental conversion count estimation

### Recommendation Engine
Outputs one of three actions:
- **promote_variant**: Variant meets confidence threshold with positive lift; recommended for rollout
- **collect_more_data**: Variant shows promise but lacks required confidence; continue experiment
- **keep_control**: No variant demonstrates reliable positive lift; iterate on creative

## API Endpoints

### `GET /api/v1/ab-testing/template`

Returns starter payload with sample control and variants.

### `POST /api/v1/ab-testing/run`

Request body:
```json
{
  "campaign_id": 700,
  "experiment_name": "Q4 CTA Test",
  "hypothesis": "Deadline urgency increases conversion.",
  "audience_size": 100000,
  "confidence_level_target": 0.95,
  "control": {
    "name": "control",
    "traffic_percentage": 0.2,
    "conversion_rate": 0.05
  },
  "variants": [
    {
      "name": "variant_urgency",
      "traffic_percentage": 0.8,
      "conversion_rate": 0.062
    }
  ]
}
```

Response includes:
- Normalized experiment arms (control + variants)
- Per-variant performance metrics (lift, confidence, z-score, p-value)
- Recommendation with action and rationale
- Dashboard-ready KPIs and chart series

## Frontend Dashboard

Available at: **http://localhost:3000/campaigns/ab-testing**

### Features
- Dynamic control and variant configuration
- Add/remove variants on the fly
- Real-time allocation visualization
- Traffic allocation and conversion rate bar charts
- Lift and confidence by variant
- Recommendation engine output panel
- JSON export of performance details

### Usage
1. Configure campaign, audience, and confidence target
2. Set control baseline and traffic allocation
3. Add variants with traffic and conversion assumptions
4. Click "Run A/B Test Analysis"
5. Review charts, metrics, and recommendation
6. Use "Load API Template" to populate default values

## Example Output

For 100k audience with 20% control (0.05 conversion) and 80% variant (0.062 conversion):

```
- Control: 20k audience, 1k conversions
- Variant: 80k audience, 4.96k conversions
- Relative Lift: 24%
- Incremental Conversions: 960
- Confidence: 100% (z-score 6.41)
- Recommendation: promote_variant
```

## Backend Implementation Details

### Service: `src/services/ab_testing.py`
- `ABTestingService.run()` orchestrates analysis
- `_normalize_allocations()` ensures traffic sums to 100%
- `_build_arms()` calculates expected outcomes per arm
- `_confidence_two_proportion()` computes statistical significance
- `_build_recommendation()` applies decision logic
- `_build_dashboard()` formats KPIs and chart data

### Schemas: `src/schemas/ab_testing.py`
- `ABTestingRequest`, `ABTestingResponse` Pydantic models
- `ControlGroupConfig`, `VariantConfig` for experiment design
- `ExperimentArm`, `VariantPerformance` for analysis results
- `Recommendation`, `ABTestingDashboard` for output

### API: `src/api/v1/endpoints/ab_testing.py`
- FastAPI router with `/template` and `/run` endpoints
- Stateless service instantiation
- Request/response validation via schemas

## Tests

Unit tests in `backend/tests/unit/`:
- `test_ab_testing_service.py`: Service logic and calculations
- `test_ab_testing_api.py`: Endpoint contract validation

Run tests:
```bash
cd backend
python -m pytest tests/unit/test_ab_testing_service.py tests/unit/test_ab_testing_api.py -v
```

## Servers

### Backend
- Running: `http://localhost:8000`
- API health: `GET /health`
- API docs: `GET /docs`

### Frontend
- Running: `http://localhost:3000`
- Home: `/`
- A/B Testing: `/campaigns/ab-testing`
- Artifacts: `/campaigns/artifacts`
- Simulation: `/campaigns/simulation`

## Architecture Alignment

- Reuses existing phase patterns (schemas, services, endpoints)
- Follows simulation service layout (template + run pattern)
- Consistent frontend page structure with artifact/simulation pages
- Shared styling and navigation integration

## Next Phase Considerations

- Persistence: Save experiments to `ABTest` entity and database
- Real-time updates: WebSocket push for live variant performance
- Sequential testing: Implement spend-optimal stopping rules
- Cohort balancing: Auto-adjust traffic based on early results
- Multi-armed bandit: Integrate Thompson Sampling for allocation

---

**Completed**: 2026-09-01
