# Phase 12 - LangSmith Observability Integration

This phase adds first-class LangSmith tracking for the campaign orchestration platform.

## Coverage

The integration tracks:

- Agent execution: status, latency, input/output payload metadata, and errors.
- Prompt execution: prompt name and content, model name, token usage, latency, and errors.
- Token consumption: input, output, and total token counters when provided by agent output schemas.
- Workflow execution: workflow lifecycle actions (start, resume, pause, manual override, graph invocation).
- Errors: execution and approval errors captured as run error fields.
- Latency: node, workflow, and agent execution duration in milliseconds.
- Approval flow: pending/approved/rejected transitions plus approver identity metadata.

## Environment Variables

Set these in backend/.env:

- LANGSMITH_TRACING: false by default. Set true to send telemetry.
- LANGSMITH_API_KEY: LangSmith API key.
- LANGSMITH_ENDPOINT: defaults to https://api.smith.langchain.com.
- LANGSMITH_PROJECT: project name used for session grouping.
- LANGSMITH_ENV: environment tag, for example dev, staging, prod.
- LANGSMITH_RELEASE: release/version tag for deployments.

## Integration Points

- backend/src/workflows/observability/langsmith.py
  - Central client wrapper with no-op safety when disabled.
- backend/src/workflows/agents/execution.py
  - Agent-level runs and prompt/token tracking.
- backend/src/workflows/orchestration/service.py
  - Workflow lifecycle and graph invocation tracking.
- backend/src/workflows/orchestration/nodes.py
  - Node-level tracking, latency, and approval-path telemetry.
- backend/src/main.py
  - Initializes tracker on startup.

## Dashboard Blueprint

Create these dashboards in LangSmith:

1. Agent Reliability Dashboard
- Filter metadata.agent_name exists
- Panels:
  - Execution count (last 24h)
  - Success vs failed status ratio
  - p50/p95 latency by agent
  - Top agent errors

2. Prompt Cost Dashboard
- Filter run_type = llm
- Panels:
  - Total input tokens by day
  - Total output tokens by day
  - Total tokens by model
  - Prompt latency distribution (p50/p95/p99)

3. Workflow Operations Dashboard
- Filter names start with workflow. or node.
- Panels:
  - Started/completed/failed workflow counts
  - Graph invoke latency trend
  - Node latency heatmap by run name
  - Manual override frequency

4. Approval Governance Dashboard
- Filter names start with approval.
- Panels:
  - Pending vs approved vs rejected counts
  - Decision latency distribution
  - Approver activity
  - Rejection reasons from metadata/comments

5. Error and SLO Dashboard
- Global filter error is not null
- Panels:
  - Error rate over time
  - p95 end-to-end workflow latency
  - Top failing nodes
  - Threshold panel for p95 latency target

## Notes

- Telemetry is fail-safe: runtime failures in LangSmith client calls do not break workflow execution.
- When LANGSMITH_TRACING is false or API key is missing, instrumentation remains local no-op.
- Token tracking depends on agent outputs carrying usage fields (token_usage or usage keys).

## Operational Runbook

For production readiness and UI validation steps, use docs/guides/PHASE12_LANGSMITH_RUNBOOK.md.
