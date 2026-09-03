"""Unit tests for Phase 5 enterprise metadata APIs."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


def _mock_metadata() -> dict:
    return {
        "source": "mock",
        "file_path": "mock.xlsx",
        "table_count": 1,
        "column_count": 2,
        "tables": [
            {
                "name": "customer",
                "description": "Customer table",
                "columns": [
                    {
                        "name": "customer_id",
                        "data_type": "int",
                        "description": "PK",
                        "nullable": False,
                        "is_primary_key": True,
                        "is_foreign_key": False,
                        "references_table": None,
                        "source_sheet": "Customer_Data",
                    },
                    {
                        "name": "household_id",
                        "data_type": "int",
                        "description": "FK",
                        "nullable": True,
                        "is_primary_key": False,
                        "is_foreign_key": True,
                        "references_table": "household",
                        "source_sheet": "Customer_Data",
                    },
                ],
            }
        ],
    }


def _mock_graph(graph_type: str) -> dict:
    return {
        "graph_type": graph_type,
        "node_count": 2,
        "edge_count": 1,
        "nodes": [
            {"id": "n1", "label": "n1", "node_type": "table", "table": "a", "column": None},
            {"id": "n2", "label": "n2", "node_type": "table", "table": "b", "column": None},
        ],
        "edges": [
            {
                "source": "n1",
                "target": "n2",
                "relationship_type": "foreign_key",
                "confidence": 1.0,
                "metadata": {},
            }
        ],
    }


@pytest.mark.asyncio
async def test_metadata_endpoints(monkeypatch) -> None:
    from src.api.v1.endpoints import metadata as metadata_endpoint

    monkeypatch.setattr(metadata_endpoint.metadata_service, "parse_data_dictionary", lambda file_path=None: _mock_metadata())
    monkeypatch.setattr(metadata_endpoint.metadata_service, "parse_database_model", lambda file_path=None: _mock_metadata())
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "build_semantic_relationship_graph",
        lambda dd, db: _mock_graph("semantic_relationship"),
    )
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "build_column_lineage_graph",
        lambda dd, db: _mock_graph("column_lineage"),
    )
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "build_table_relationship_graph",
        lambda db: _mock_graph("table_relationship"),
    )
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "generate_sql",
        lambda base_table, select_columns, filters, table_relationship_graph, limit=100: {
            "sql": "SELECT customer.customer_id FROM customer LIMIT 10;",
            "joined_tables": ["customer"],
            "unresolved_columns": [],
        },
    )
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "generate_waterfall_analysis",
        lambda base_table, entity_id_column, stages: {
            "sql": "SELECT 'base' AS stage_name, 100 AS stage_count;",
            "stage_count": len(stages),
            "stage_names": [s["name"] for s in stages],
        },
    )
    monkeypatch.setattr(
        metadata_endpoint.metadata_service,
        "generate_explainability_report",
        lambda sql, semantic_graph, lineage_graph, table_relationship_graph: {
            "summary": "Traceable output.",
            "assumptions": ["authoritative metadata"],
            "lineage_coverage": {"nodes": 1, "edges": 1},
            "relationship_coverage": {"nodes": 1, "edges": 1},
            "semantic_coverage": {"nodes": 1, "edges": 1},
        },
    )

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert (await client.post("/api/v1/metadata/parse/data-dictionary", json={})).status_code == 200
        assert (await client.post("/api/v1/metadata/parse/database-model", json={})).status_code == 200
        assert (await client.post("/api/v1/metadata/graphs/semantic", json={})).status_code == 200
        assert (await client.post("/api/v1/metadata/graphs/lineage", json={})).status_code == 200
        assert (await client.post("/api/v1/metadata/graphs/table-relationships", json={})).status_code == 200

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
        assert "sql" in sql_response.json()

        waterfall_response = await client.post(
            "/api/v1/metadata/waterfall/generate",
            json={
                "base_table": "interaction_history",
                "entity_id_column": "customer_id",
                "stages": [{"name": "contacted", "condition": "t.channel = 'email'"}],
            },
        )
        assert waterfall_response.status_code == 200
        assert waterfall_response.json()["stage_count"] == 1

        explainability_response = await client.post(
            "/api/v1/metadata/explainability/report",
            json={
                "sql": "SELECT 1;",
                "semantic_graph": _mock_graph("semantic_relationship"),
                "lineage_graph": _mock_graph("column_lineage"),
                "table_relationship_graph": _mock_graph("table_relationship"),
            },
        )
        assert explainability_response.status_code == 200
        assert "summary" in explainability_response.json()
