"""Unit tests for Phase 6 campaign artifact API endpoints."""
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app
from src.services.artifact_generation import CampaignArtifactService


@pytest.mark.asyncio
async def test_campaign_artifact_endpoints(tmp_path: Path, monkeypatch) -> None:
    from src.api.v1.endpoints import campaign_artifacts as artifact_endpoint

    monkeypatch.setattr(
        artifact_endpoint,
        "artifact_service",
        CampaignArtifactService(base_dir=tmp_path / "artifact_api"),
    )

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/api/v1/campaign-artifacts/500/generate",
            json={
                "artifact_type": "selection_briefing",
                "content": {"objective": "upsell"},
                "author": "planner.user",
            },
        )
        assert create_response.status_code == 200
        assert create_response.json()["version"] == 1

        submit_response = await client.post(
            "/api/v1/campaign-artifacts/500/selection_briefing/approval/submit",
            json={},
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "pending_approval"

        review_response = await client.post(
            "/api/v1/campaign-artifacts/500/selection_briefing/approval/review",
            json={"reviewer": "manager.user", "approve": True, "comment": "approved"},
        )
        assert review_response.status_code == 200
        assert review_response.json()["status"] == "approved"

        create_second = await client.post(
            "/api/v1/campaign-artifacts/500/generate",
            json={
                "artifact_type": "selection_briefing",
                "content": {"objective": "cross-sell"},
                "author": "planner.user",
            },
        )
        assert create_second.status_code == 200
        assert create_second.json()["version"] == 2

        rollback_response = await client.post(
            "/api/v1/campaign-artifacts/500/selection_briefing/rollback",
            json={"target_version": 1, "actor": "ops.user"},
        )
        assert rollback_response.status_code == 200
        assert rollback_response.json()["status"] == "rolled_back"
        assert rollback_response.json()["version"] == 3

        versions_response = await client.get(
            "/api/v1/campaign-artifacts/500/selection_briefing/versions",
        )
        assert versions_response.status_code == 200
        assert len(versions_response.json()) == 3

        excel_response = await client.post(
            "/api/v1/campaign-artifacts/500/exports/excel",
            json={},
        )
        assert excel_response.status_code == 200
        assert excel_response.json()["path"].endswith(".xlsx")

        word_response = await client.post(
            "/api/v1/campaign-artifacts/500/exports/word",
            json={},
        )
        assert word_response.status_code == 200
        assert word_response.json()["path"].endswith(".docx")


@pytest.mark.asyncio
async def test_campaign_artifact_endpoints_db_backend_toggle(monkeypatch) -> None:
    from src.api.v1.endpoints import campaign_artifacts as artifact_endpoint

    class _FakeDbArtifact:
        def __init__(self) -> None:
            self.id = 77
            self.campaign_id = 600
            self.artifact_type = type("_T", (), {"value": "selection_briefing"})()
            self.title = "Selection Briefing"
            self.version = 1
            self.status = type("_S", (), {"value": "draft"})()
            self.content = {"objective": "db-backed"}
            self.author = "db.user"
            self.approver = None
            self.approval_comment = None
            self.created_at = "2026-09-01T00:00:00+00:00"
            self.updated_at = "2026-09-01T00:00:00+00:00"

    class FakeDbService:
        def __init__(self, session) -> None:  # noqa: ANN001
            self._artifact = _FakeDbArtifact()

        async def generate_artifact(self, campaign_id, artifact_type, content, author):  # noqa: ANN001
            return self._artifact

        async def list_versions(self, campaign_id, artifact_type):  # noqa: ANN001
            return [self._artifact]

        async def get_current(self, campaign_id, artifact_type):  # noqa: ANN001
            return self._artifact

        async def submit_for_approval(self, campaign_id, artifact_type):  # noqa: ANN001
            self._artifact.status = type("_S", (), {"value": "pending_approval"})()
            return self._artifact

        async def review_approval(self, campaign_id, artifact_type, reviewer, approve, comment=None):  # noqa: ANN001
            self._artifact.status = type("_S", (), {"value": "approved" if approve else "rejected"})()
            self._artifact.approver = reviewer
            self._artifact.approval_comment = comment
            return self._artifact

        async def rollback_to_version(self, campaign_id, artifact_type, target_version, actor):  # noqa: ANN001
            self._artifact.status = type("_S", (), {"value": "rolled_back"})()
            self._artifact.version = 2
            return self._artifact

        async def export_excel(self, campaign_id):  # noqa: ANN001
            return Path("/tmp/fake.xlsx")

        async def export_word(self, campaign_id):  # noqa: ANN001
            return Path("/tmp/fake.docx")

    async def _fake_get_db():
        yield object()

    monkeypatch.setattr(artifact_endpoint, "CampaignArtifactDbService", FakeDbService)
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/cvm_catalyst")
    monkeypatch.setattr(artifact_endpoint.settings, "ARTIFACT_PERSISTENCE_BACKEND", "db")

    app = create_app()
    app.dependency_overrides[artifact_endpoint.get_db] = _fake_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/api/v1/campaign-artifacts/600/generate",
            json={
                "artifact_type": "selection_briefing",
                "content": {"objective": "db"},
                "author": "db.user",
            },
        )
        assert create_response.status_code == 200
        assert create_response.json()["id"] == "77"

        versions_response = await client.get("/api/v1/campaign-artifacts/600/selection_briefing/versions")
        assert versions_response.status_code == 200
        assert len(versions_response.json()) == 1

        excel_response = await client.post("/api/v1/campaign-artifacts/600/exports/excel", json={})
        assert excel_response.status_code == 200
        assert excel_response.json()["path"].endswith(".xlsx")

    monkeypatch.setattr(artifact_endpoint.settings, "ARTIFACT_PERSISTENCE_BACKEND", "file")


@pytest.mark.asyncio
async def test_campaign_artifact_db_mode_falls_back_to_file_without_database_url(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from src.api.v1.endpoints import campaign_artifacts as artifact_endpoint

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(artifact_endpoint.settings, "ARTIFACT_PERSISTENCE_BACKEND", "db")
    monkeypatch.setattr(
        artifact_endpoint,
        "artifact_service",
        CampaignArtifactService(base_dir=tmp_path / "artifact_api_fallback"),
    )

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/api/v1/campaign-artifacts/700/generate",
            json={
                "artifact_type": "selection_briefing",
                "content": {"objective": "fallback-file-mode"},
                "author": "local.user",
            },
        )
        assert create_response.status_code == 200
        assert create_response.json()["version"] == 1

    monkeypatch.setattr(artifact_endpoint.settings, "ARTIFACT_PERSISTENCE_BACKEND", "file")
