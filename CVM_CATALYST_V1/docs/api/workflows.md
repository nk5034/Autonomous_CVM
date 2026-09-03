# Workflow Orchestration API (Phase 7)

Base path: /api/v1/workflows

This API runs the LangGraph campaign orchestration workflow and exposes a compact Phase 7 testing-platform summary in responses.

## Start Workflow Run

POST /start

Request body:

{
  "campaign_id": 12001,
  "workflow_id": "wf_phase7_12001"
}

Example response:

{
  "workflow_id": "wf_phase7_12001",
  "campaign_id": 12001,
  "status": "running",
  "current_node": "testing_platform",
  "next_node": "simulation",
  "awaiting_approval": false,
  "last_error": null,
  "phase7_testing_platform": {
    "status": "success",
    "execution_summary": {
      "total": 12,
      "passed": 11,
      "failed": 1,
      "pass_rate": 91.67,
      "started_at": "2026-09-01T09:30:00Z",
      "completed_at": "2026-09-01T09:30:04Z"
    },
    "report_summary": {
      "run_id": "run_1788245404",
      "total_tests": 12,
      "passed_tests": 11,
      "failed_tests": 1,
      "pass_rate": 91.67
    },
    "audit_event_count": 5
  }
}

## Resume Workflow Run

POST /{workflow_id}/resume

Resumes a paused or waiting-approval workflow and returns the latest state snapshot.

Not found response:

{
  "detail": "Workflow state not found for workflow_id='wf_phase7_12001'."
}

## Approve Workflow Node

POST /{workflow_id}/approve

Request body:

{
  "approver": "ops_user",
  "decision": "approved",
  "comment": "Looks good"
}

Behavior:

- Records decision for the pending approval node.
- Triggers continuation when decision is approved.
- Marks workflow failed when decision is rejected.

Validation errors:

{
  "detail": "decision must be one of: pending, approved, rejected"
}

## Get Workflow State

GET /{workflow_id}

Returns latest persisted state for the workflow, including the Phase 7 summary if the testing-platform node has executed.

Not found response:

{
  "detail": "Workflow state not found."
}

## Phase 7 Summary Fields

The response field phase7_testing_platform is populated from workflow artifacts.testing_platform and includes:

- status: success or failed
- execution_summary: quick execution metrics from the test runner
- report_summary: aggregate report metrics
- audit_event_count: number of audit trail events captured during platform execution

## Phase 12 LangSmith Telemetry

Workflow orchestration now emits LangSmith telemetry for:

- workflow lifecycle events (`workflow.start`, `workflow.resume`, `workflow.pause`, graph invocation)
- node execution latency and errors (`node.*` events)
- approval flow transitions (`approval.business_approval` and pending/approved/rejected metadata)

Agent execution telemetry is also emitted from the agent execution manager, including prompt and token usage tracking when usage metadata exists in agent outputs.

For setup and dashboard templates, see docs/PHASE12_LANGSMITH.md.
