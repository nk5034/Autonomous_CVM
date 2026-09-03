# A/B Testing API

Phase 10 introduces an experimentation framework for campaign optimization.

## Endpoints

### GET /api/v1/ab-testing/template

Returns a starter payload with control configuration, treatment variants, and confidence target.

### POST /api/v1/ab-testing/run

Evaluates an experiment configuration and returns:

- normalized traffic allocation
- expected conversions per arm
- statistical confidence (two-proportion z-test)
- lift analysis by variant
- recommendation engine output
- dashboard-ready KPI and chart series

## Core Inputs

- control group name, traffic percentage, conversion rate
- one or more variants with traffic and conversion assumptions
- confidence threshold for significance decisioning
- total audience size

## Core Outputs

- control and variant arms with allocations and audiences
- per-variant lift and absolute lift versus control
- p-value and derived confidence score
- recommendation action: promote_variant, collect_more_data, or keep_control