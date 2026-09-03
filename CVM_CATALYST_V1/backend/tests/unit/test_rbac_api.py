"""Unit tests for Phase 13 RBAC route permissions and auditing."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


@pytest.mark.asyncio
async def test_ab_testing_rbac_by_role(monkeypatch) -> None:
    from src.api.v1.endpoints import ab_testing as ab_testing_endpoint

    monkeypatch.setattr(
        ab_testing_endpoint.ab_testing_service,
        "run",
        lambda payload: {
            "experiment_id": "rbac_ab_001",
            "generated_at": "2026-09-02T00:00:00+00:00",
            "campaign_id": payload.campaign_id,
            "experiment_name": payload.experiment_name,
            "hypothesis": payload.hypothesis,
            "confidence_level_target": payload.confidence_level_target,
            "arms": [
                {
                    "name": "control",
                    "is_control": True,
                    "allocation": 0.2,
                    "audience": 200,
                    "conversion_rate": 0.05,
                    "expected_conversions": 10,
                },
                {
                    "name": "variant_a",
                    "is_control": False,
                    "allocation": 0.8,
                    "audience": 800,
                    "conversion_rate": 0.06,
                    "expected_conversions": 48,
                },
            ],
            "variant_performance": [
                {
                    "name": "variant_a",
                    "lift": 0.2,
                    "absolute_lift": 0.01,
                    "z_score": 2.1,
                    "p_value": 0.03,
                    "confidence": 0.97,
                    "statistically_significant": True,
                    "incremental_conversions": 8,
                }
            ],
            "recommendation": {
                "action": "promote_variant",
                "rationale": "statistically significant lift",
                "recommended_variant": "variant_a",
            },
            "dashboard": {
                "kpis": [{"label": "Audience", "value": 1000, "format": "number"}],
                "traffic_allocation": [{"label": "control", "value": 0.2}],
                "conversion_rates": [{"label": "control", "value": 0.05}],
                "lift_by_variant": [{"label": "variant_a", "value": 0.2}],
                "confidence_by_variant": [{"label": "variant_a", "value": 0.97}],
            },
        },
    )

    payload = {
        "campaign_id": 1,
        "experiment_name": "RBAC test",
        "hypothesis": "A outperforms control",
        "audience_size": 1000,
        "confidence_level_target": 0.95,
        "control": {"name": "control", "traffic_percentage": 0.2, "conversion_rate": 0.05},
        "variants": [{"name": "variant_a", "traffic_percentage": 0.8, "conversion_rate": 0.06}],
    }

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        denied_response = await client.post(
            "/api/v1/ab-testing/run",
            headers={"X-User-Role": "Business User", "X-User-Id": "101"},
            json=payload,
        )
        assert denied_response.status_code == 403

        allowed_response = await client.post(
            "/api/v1/ab-testing/run",
            headers={"X-User-Role": "Campaign Manager", "X-User-Id": "102"},
            json=payload,
        )
        assert allowed_response.status_code == 200
        assert allowed_response.json()["experiment_id"] == "rbac_ab_001"


@pytest.mark.asyncio
async def test_workflow_approval_rbac_by_role(monkeypatch) -> None:
    from src.api.v1.endpoints import workflow as workflow_endpoint
    from src.workflows.orchestration.state import CampaignState

    class FakeOrchestrator:
        def approve(self, workflow_id: str, approver: str, decision: str, comment: str | None = None) -> CampaignState:
            return CampaignState(campaign_id=123, workflow_id=workflow_id, thread_id="thread-approval")

    monkeypatch.setattr(workflow_endpoint, "orchestrator", FakeOrchestrator())

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        manager_response = await client.post(
            "/api/v1/workflows/wf_rbac_001/approve",
            headers={"X-User-Role": "Campaign Manager", "X-User-Id": "201"},
            json={"approver": "manager", "decision": "approved", "comment": "ok"},
        )
        assert manager_response.status_code == 403

        approver_response = await client.post(
            "/api/v1/workflows/wf_rbac_001/approve",
            headers={"X-User-Role": "Approver", "X-User-Id": "202"},
            json={"approver": "approver", "decision": "approved", "comment": "approved"},
        )
        assert approver_response.status_code == 200
        assert approver_response.json()["workflow_id"] == "wf_rbac_001"


@pytest.mark.asyncio
async def test_denied_access_generates_audit_event(monkeypatch) -> None:
    from src.api.v1.endpoints import ab_testing as ab_testing_endpoint
    from src.core.security import rbac as rbac_module

    monkeypatch.setattr(ab_testing_endpoint.ab_testing_service, "run", lambda payload: payload)

    audit_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(rbac_module, "_persist_audit_event", audit_mock)

    payload = {
        "campaign_id": 1,
        "experiment_name": "RBAC audit",
        "hypothesis": "A outperforms control",
        "audience_size": 1000,
        "confidence_level_target": 0.95,
        "control": {"name": "control", "traffic_percentage": 0.2, "conversion_rate": 0.05},
        "variants": [{"name": "variant_a", "traffic_percentage": 0.8, "conversion_rate": 0.06}],
    }

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/ab-testing/run",
            headers={"X-User-Role": "Business User", "X-User-Id": "301", "X-User-Email": "a@b.com"},
            json=payload,
        )

    assert response.status_code == 403
    assert audit_mock.await_count >= 1
    assert audit_mock.await_args.kwargs["allowed"] is False
