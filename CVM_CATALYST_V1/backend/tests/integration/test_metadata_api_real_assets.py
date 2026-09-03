"""Integration tests for metadata API endpoints with real knowledge assets."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


def _knowledge_file(name: str) -> str:
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "knowledge" / name
    assert path.exists(), f"Required knowledge asset missing: {path}"
    return str(path)


@pytest.mark.asyncio
async def test_metadata_api_real_asset_flow() -> None:
    transport = ASGITransport(app=create_app())

    dd_path = _knowledge_file("Data Dictionary.xlsx")
    db_path = _knowledge_file("Database Model.xlsx")

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        dd_response = await client.post("/api/v1/metadata/parse/data-dictionary", json={"file_path": dd_path})
        assert dd_response.status_code == 200
        dd = dd_response.json()
        assert dd["source"] == "data_dictionary"
        assert dd["table_count"] > 0

        db_response = await client.post("/api/v1/metadata/parse/database-model", json={"file_path": db_path})
        assert db_response.status_code == 200
        db = db_response.json()
        assert db["source"] == "database_model"
        assert db["column_count"] > 0

        semantic_response = await client.post("/api/v1/metadata/graphs/semantic", json={"file_path": dd_path})
        assert semantic_response.status_code == 200
        semantic = semantic_response.json()
        assert semantic["graph_type"] == "semantic_relationship"

        lineage_response = await client.post("/api/v1/metadata/graphs/lineage", json={"file_path": dd_path})
        assert lineage_response.status_code == 200
        lineage = lineage_response.json()
        assert lineage["graph_type"] == "column_lineage"

        table_graph_response = await client.post(
            "/api/v1/metadata/graphs/table-relationships", json={"file_path": db_path}
        )
        assert table_graph_response.status_code == 200
        table_graph = table_graph_response.json()
        assert table_graph["graph_type"] == "table_relationship"

        sql_response = await client.post(
            "/api/v1/metadata/sql/generate",
            json={
                "base_table": "customer",
                "select_columns": ["customer.customer_id"],
                "filters": {},
                "limit": 10,
            },
        )
        assert sql_response.status_code == 200
        sql_payload = sql_response.json()
        assert sql_payload["sql"] == "SELECT customer.customer_id\nFROM customer\n\nLIMIT 10;"

        waterfall_response = await client.post(
            "/api/v1/metadata/waterfall/generate",
            json={
                "base_table": "customer",
                "entity_id_column": "customer_id",
                "stages": [{"name": "non_null", "condition": "t.customer_id IS NOT NULL"}],
            },
        )
        assert waterfall_response.status_code == 200
        waterfall_payload = waterfall_response.json()
        assert waterfall_payload["stage_count"] == 1

        explainability_response = await client.post(
            "/api/v1/metadata/explainability/report",
            json={
                "sql": sql_payload["sql"],
                "semantic_graph": semantic,
                "lineage_graph": lineage,
                "table_relationship_graph": table_graph,
            },
        )
        assert explainability_response.status_code == 200
        explainability_payload = explainability_response.json()
        assert "traceable" in explainability_payload["summary"].lower()
        assert "semantic_coverage" in explainability_payload
        assert "lineage_coverage" in explainability_payload
        assert "relationship_coverage" in explainability_payload
        assert "sql_preview" not in explainability_payload
