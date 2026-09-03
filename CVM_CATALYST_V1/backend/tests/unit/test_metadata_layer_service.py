"""Unit tests for enterprise metadata services (Phase 5)."""
from src.services.metadata_layer import EnterpriseMetadataService


def _sample_data_dictionary() -> dict:
    service = EnterpriseMetadataService()
    parsed = service.parse_data_dictionary_rows(
        rows=[
            {
                "table_name": "customer",
                "column_name": "customer_id",
                "data_type": "int",
                "description": "Primary customer identifier",
                "nullable": "no",
            },
            {
                "table_name": "customer",
                "column_name": "household_id",
                "data_type": "int",
                "description": "Household key",
                "nullable": "yes",
            },
            {
                "table_name": "subscription",
                "column_name": "customer_id",
                "data_type": "int",
                "description": "Foreign key to customer",
                "nullable": "no",
            },
        ],
        file_path="inline-dd",
        source_sheet="Rich_Data_Dictionary",
    )
    return service._to_response(parsed)  # noqa: SLF001 - test uses canonical serialization


def _sample_database_model() -> dict:
    service = EnterpriseMetadataService()
    customer = service.parse_database_model_rows(
        rows=[
            {
                "column_name": "customer_id",
                "data_type": "int",
                "key_type": "PK",
            },
            {
                "column_name": "household_id",
                "data_type": "int",
                "key_type": "FK",
                "references_table": "household",
            },
        ],
        sheet_name="Customer_Data",
    )
    subscription = service.parse_database_model_rows(
        rows=[
            {
                "column_name": "subscription_id",
                "data_type": "int",
                "key_type": "PK",
            },
            {
                "column_name": "customer_id",
                "data_type": "int",
                "key_type": "FK",
                "references_table": "customer",
            },
        ],
        sheet_name="Subscription_Data",
    )
    household = service.parse_database_model_rows(
        rows=[{"column_name": "id", "data_type": "int", "key_type": "PK"}],
        sheet_name="Household_Data",
    )

    all_tables = {}
    all_tables.update(customer)
    all_tables.update(subscription)
    all_tables.update(household)

    parsed = {
        "source": "database_model",
        "file_path": "inline-db",
        "table_count": len(all_tables),
        "column_count": sum(len(table.columns) for table in all_tables.values()),
        "tables": [
            {
                "name": table.name,
                "description": table.description,
                "columns": [
                    {
                        "name": c.name,
                        "data_type": c.data_type,
                        "description": c.description,
                        "nullable": c.nullable,
                        "is_primary_key": c.is_primary_key,
                        "is_foreign_key": c.is_foreign_key,
                        "references_table": c.references_table,
                        "source_sheet": c.source_sheet,
                    }
                    for c in table.columns.values()
                ],
            }
            for table in all_tables.values()
        ],
    }
    return parsed


def test_build_semantic_relationship_graph() -> None:
    service = EnterpriseMetadataService()
    dd = _sample_data_dictionary()
    db = _sample_database_model()

    graph = service.build_semantic_relationship_graph(dd, db)

    assert graph["graph_type"] == "semantic_relationship"
    assert graph["node_count"] > 0
    assert any(edge["relationship_type"].startswith("maps_to") for edge in graph["edges"])


def test_build_column_lineage_graph() -> None:
    service = EnterpriseMetadataService()
    dd = _sample_data_dictionary()
    db = _sample_database_model()

    graph = service.build_column_lineage_graph(dd, db)

    assert graph["graph_type"] == "column_lineage"
    assert graph["edge_count"] > 0
    assert all(edge["relationship_type"] == "column_lineage" for edge in graph["edges"])


def test_build_table_relationship_graph() -> None:
    service = EnterpriseMetadataService()
    db = _sample_database_model()

    graph = service.build_table_relationship_graph(db)

    assert graph["graph_type"] == "table_relationship"
    assert graph["node_count"] >= 3
    assert any(edge["relationship_type"] in {"foreign_key", "inferred_foreign_key"} for edge in graph["edges"])


def test_generate_sql() -> None:
    service = EnterpriseMetadataService()
    db = _sample_database_model()
    table_graph = service.build_table_relationship_graph(db)

    generated = service.generate_sql(
        base_table="subscription",
        select_columns=["subscription.subscription_id", "customer.customer_id"],
        filters={"subscription.subscription_id": 123},
        table_relationship_graph=table_graph,
        limit=50,
    )

    assert "FROM subscription" in generated["sql"]
    assert "LEFT JOIN customer" in generated["sql"]
    assert "LIMIT 50" in generated["sql"]


def test_generate_waterfall_analysis() -> None:
    service = EnterpriseMetadataService()
    generated = service.generate_waterfall_analysis(
        base_table="interaction_history",
        entity_id_column="customer_id",
        stages=[
            {"name": "contacted", "condition": "t.channel = 'email'"},
            {"name": "responded", "condition": "t.response_flag = 1"},
        ],
    )

    assert generated["stage_count"] == 2
    assert "WITH" in generated["sql"]
    assert "responded" in generated["sql"]


def test_generate_explainability_report() -> None:
    service = EnterpriseMetadataService()

    semantic = {
        "graph_type": "semantic_relationship",
        "node_count": 2,
        "edge_count": 1,
        "nodes": [],
        "edges": [],
    }
    lineage = {
        "graph_type": "column_lineage",
        "node_count": 2,
        "edge_count": 1,
        "nodes": [],
        "edges": [],
    }
    table_graph = {
        "graph_type": "table_relationship",
        "node_count": 2,
        "edge_count": 1,
        "nodes": [],
        "edges": [],
    }

    report = service.generate_explainability_report(
        sql="SELECT 1;",
        semantic_graph=semantic,
        lineage_graph=lineage,
        table_relationship_graph=table_graph,
    )

    assert "traceable" in report["summary"].lower()
    assert report["semantic_coverage"]["edges"] == 1
    assert len(report["assumptions"]) >= 1
