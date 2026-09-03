# Phase 12 LangSmith Runbook

This runbook covers final operational completion of Phase 12:

- Configure LangSmith environment variables
- Validate telemetry emission from backend
- Create required dashboards
- Execute a smoke test and acceptance checklist

## 1. Prerequisites

- LangSmith account and API key
- Local backend dependencies installed in workspace venv
- Backend service running

## 2. Environment Setup

Copy and configure backend environment values:

```bash
cd backend
cp .env.example .env
```

Set these variables in `backend/.env`:

- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY=<your_api_key>`
- `LANGSMITH_ENDPOINT=https://api.smith.langchain.com`
- `LANGSMITH_PROJECT=cvm-catalyst`
- `LANGSMITH_ENV=dev` (or staging/prod)
- `LANGSMITH_RELEASE=phase12`

## 3. Start Backend With Workspace venv

From repository root:

```bash
cd backend
../.venv/Scripts/python -m uvicorn src.main:app --reload
```

Expected startup signal in logs:

- `LangSmith tracing enabled: True`

## 4. Generate Telemetry Events

In a second terminal, trigger workflow APIs:

```bash
API_BASE_URL="http://localhost:8000/api/v1"

curl -X POST "$API_BASE_URL/workflows/start" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 12001,
    "workflow_id": "wf_phase12_12001"
  }'

curl -X POST "$API_BASE_URL/workflows/wf_phase12_12001/resume"

curl "$API_BASE_URL/workflows/wf_phase12_12001"
```

Optional approval-path telemetry generation:

```bash
curl -X POST "$API_BASE_URL/workflows/wf_phase12_12001/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "approver": "ops_user",
    "decision": "approved",
    "comment": "Looks good"
  }'
```

## 5. Verify Telemetry in LangSmith

Open LangSmith project `cvm-catalyst` and verify runs appear for:

- Workflow events: names like `workflow.start`, `workflow.resume`, `workflow.graph.invoke`
- Node events: names starting with `node.`
- Agent events: names starting with `agent.`
- Prompt events: `run_type=llm`
- Approval events: names starting with `approval.`

Check run metadata includes:

- `workflow_id`
- `campaign_id`
- `latency_ms`
- `status`
- `environment`
- `release`

Check error capture:

- Failed runs should include non-empty `error` field.

Check token capture:

- LLM runs include `metadata.token_usage.input_tokens`
- LLM runs include `metadata.token_usage.output_tokens`
- LLM runs include `metadata.token_usage.total_tokens`

## 6. Dashboard Creation Checklist

Create these five dashboards in LangSmith:

1. Agent Reliability
- Filters: `metadata.agent_name exists`
- Metrics: run count, success/failure ratio, p50/p95 latency, top errors

2. Prompt Cost
- Filters: `run_type=llm`
- Metrics: input tokens/day, output tokens/day, total tokens by model, p50/p95/p99 latency

3. Workflow Operations
- Filters: `name starts with workflow.` OR `name starts with node.`
- Metrics: workflow state counts, graph invoke latency, node latency heatmap, manual override frequency

4. Approval Governance
- Filters: `name starts with approval.`
- Metrics: pending/approved/rejected, decision latency, approver activity, rejection reasons

5. Error and SLO
- Filters: `error is not null`
- Metrics: error rate trend, p95 end-to-end latency, top failing nodes, SLO threshold status

## 7. Acceptance Criteria

Phase 12 is operationally complete when all are true:

- [ ] `LANGSMITH_TRACING=true` in active backend environment
- [ ] Backend emits runs visible in LangSmith project
- [ ] Agent, prompt, workflow, approval events are all present
- [ ] Latency and error data are present on relevant runs
- [ ] Token usage appears on prompt runs (when usage is available)
- [ ] All five dashboards are created and populated with recent data
- [ ] At least one end-to-end workflow execution has been validated in UI

## 8. Troubleshooting

No runs appearing:

- Confirm `LANGSMITH_TRACING=true`
- Confirm `LANGSMITH_API_KEY` is valid
- Confirm project name matches `LANGSMITH_PROJECT`
- Confirm backend process restarted after `.env` update

Runs appear but no prompt tokens:

- Verify agent output includes `token_usage` or `usage`
- Verify prompt path in agent execution manager was invoked

Errors missing:

- Confirm exceptions propagate through tracker update paths
- Validate failed scenarios by submitting invalid approval decision or forcing agent failure in a safe test
