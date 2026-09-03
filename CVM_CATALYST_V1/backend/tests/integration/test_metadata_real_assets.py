"""Integration tests for enterprise metadata layer using real knowledge assets."""

from __future__ import annotations

from pathlib import Path

from src.services.metadata_layer import EnterpriseMetadataService


def _knowledge_file(name: str) -> str:
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "knowledge" / name
    assert path.exists(), f"Required knowledge asset missing: {path}"
    return str(path)


def test_real_metadata_workbooks_parse() -> None:
    service = EnterpriseMetadataService()

    data_dictionary = service.parse_data_dictionary(_knowledge_file("Data Dictionary.xlsx"))
    database_model = service.parse_database_model(_knowledge_file("Database Model.xlsx"))

    assert data_dictionary["source"] == "data_dictionary"
    assert database_model["source"] == "database_model"
    assert data_dictionary["table_count"] > 0
    assert data_dictionary["column_count"] > 0
    assert database_model["table_count"] > 0
    assert database_model["column_count"] > 0


def test_real_metadata_pipeline_builds_artifacts() -> None:
    service = EnterpriseMetadataService()

    data_dictionary = service.parse_data_dictionary(_knowledge_file("Data Dictionary.xlsx"))
    database_model = service.parse_database_model(_knowledge_file("Database Model.xlsx"))

    semantic_graph = service.build_semantic_relationship_graph(data_dictionary, database_model)
    lineage_graph = service.build_column_lineage_graph(data_dictionary, database_model)
    table_graph = service.build_table_relationship_graph(database_model)

    assert semantic_graph["graph_type"] == "semantic_relationship"
    assert lineage_graph["graph_type"] == "column_lineage"
    assert table_graph["graph_type"] == "table_relationship"
    assert semantic_graph["node_count"] > 0
    assert lineage_graph["node_count"] > 0
    assert table_graph["node_count"] > 0

    table_with_columns = next(
        (table for table in database_model["tables"] if table["columns"]),
        None,
    )
    assert table_with_columns is not None

    base_table = table_with_columns["name"]
    first_column = table_with_columns["columns"][0]["name"]

    generated_sql = service.generate_sql(
        base_table=base_table,
        select_columns=[f"{base_table}.{first_column}"],
        filters={},
        table_relationship_graph=table_graph,
        limit=25,
    )
    assert "SELECT" in generated_sql["sql"]
    assert "FROM" in generated_sql["sql"]
    assert f"LIMIT {25}" in generated_sql["sql"]

    waterfall = service.generate_waterfall_analysis(
        base_table=base_table,
        entity_id_column=first_column,
        stages=[
            {
                "name": "non_null_entity",
                "condition": f"t.{first_column} IS NOT NULL",
            }
        ],
    )
    assert waterfall["stage_count"] == 1
    assert "WITH" in waterfall["sql"]

    report = service.generate_explainability_report(
        sql=generated_sql["sql"],
        semantic_graph=semantic_graph,
        lineage_graph=lineage_graph,
        table_relationship_graph=table_graph,
    )
    assert "traceable" in report["summary"].lower()
    assert report["semantic_coverage"]["nodes"] >= 0
    assert report["lineage_coverage"]["nodes"] >= 0
    assert report["relationship_coverage"]["nodes"] >= 0


def test_deterministic_sql_and_explainability_subset() -> None:
    service = EnterpriseMetadataService()
    database_model = service.parse_database_model(_knowledge_file("Database Model.xlsx"))
    table_graph = service.build_table_relationship_graph(database_model)

    generated_sql = service.generate_sql(
        base_table="customer",
        select_columns=["customer.customer_id"],
        filters={},
        table_relationship_graph=table_graph,
        limit=10,
    )

    expected_sql = "SELECT customer.customer_id\nFROM customer\n\nLIMIT 10;"
    assert generated_sql["sql"] == expected_sql
    assert generated_sql["joined_tables"] == ["customer"]
    assert generated_sql["unresolved_columns"] == []

    report = service.generate_explainability_report(
        sql=generated_sql["sql"],
        semantic_graph={
            "graph_type": "semantic_relationship",
            "node_count": 2,
            "edge_count": 1,
            "nodes": [],
            "edges": [],
        },
        lineage_graph={
            "graph_type": "column_lineage",
            "node_count": 2,
            "edge_count": 1,
            "nodes": [],
            "edges": [],
        },
        table_relationship_graph={
            "graph_type": "table_relationship",
            "node_count": 2,
            "edge_count": 1,
            "nodes": [],
            "edges": [],
        },
    )

    assert report["summary"].startswith("Generated SQL is traceable")
    assert report["semantic_coverage"] == {"nodes": 2, "edges": 1}
    assert report["lineage_coverage"] == {"nodes": 2, "edges": 1}
    assert report["relationship_coverage"] == {"nodes": 2, "edges": 1}
    assert report["sql_preview"] == ["SELECT customer.customer_id", "FROM customer", "", "LIMIT 10;"]
