# Backend - CVM Catalyst

FastAPI backend with LangGraph orchestration and CrewAI agents.

## Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

## Environment

Copy `.env.example` to `.env` and configure.

LangSmith observability (Phase 12):
- `LANGSMITH_TRACING=true` to enable telemetry emission
- `LANGSMITH_API_KEY` for authentication
- `LANGSMITH_ENDPOINT` defaults to `https://api.smith.langchain.com`
- `LANGSMITH_PROJECT`, `LANGSMITH_ENV`, and `LANGSMITH_RELEASE` for project/environment/release tagging

Artifact persistence backend:
- `ARTIFACT_PERSISTENCE_BACKEND=file` for local filesystem persistence (default)
- `ARTIFACT_PERSISTENCE_BACKEND=db` for SQLAlchemy/Alembic-backed persistence

When using `db`, run migrations before starting the API.

Local migration sequence:

```bash
# From repository root
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres

# From backend/
python -m alembic upgrade head
```

## Running

```bash
uvicorn src.main:app --reload
```

## Workflow API Quick Examples

Base URL:

```bash
export API_BASE_URL="http://localhost:8000/api/v1"
```

Start workflow run:

```bash
curl -X POST "$API_BASE_URL/workflows/start" \
	-H "Content-Type: application/json" \
	-d '{
		"campaign_id": 12001,
		"workflow_id": "wf_phase7_12001"
	}'
```

Resume workflow run:

```bash
curl -X POST "$API_BASE_URL/workflows/wf_phase7_12001/resume"
```

Get workflow state:

```bash
curl "$API_BASE_URL/workflows/wf_phase7_12001"
```

Inspect Phase 7 testing-platform summary from the response payload:

- phase7_testing_platform.status
- phase7_testing_platform.execution_summary
- phase7_testing_platform.report_summary
- phase7_testing_platform.audit_event_count

## LangSmith Dashboards (Phase 12)

Dashboard blueprint and trace taxonomy are documented in ../docs/PHASE12_LANGSMITH.md.

## Synthetic Data API Quick Examples (Phase 8)

Get generation template:

```bash
curl "$API_BASE_URL/synthetic-data/config/template"
```

Generate synthetic data:

```bash
curl -X POST "$API_BASE_URL/synthetic-data/generate" \
	-H "Content-Type: application/json" \
	-d '{
		"volume": {
			"customer_count": 1000,
			"household_coverage_ratio": 0.45,
			"avg_subscriptions_per_customer": 1.2,
			"avg_interactions_per_customer": 6,
			"channel_response_rate": 0.28,
			"conversion_rate": 0.08,
			"record_overrides": {}
		},
		"random_seed": 42,
		"include_records": false,
		"max_inline_records_per_dataset": 200
	}'
```
