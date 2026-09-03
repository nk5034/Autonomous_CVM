# Enterprise Metadata Layer API

Phase 5 introduces an enterprise metadata layer where the Data Dictionary and Database Model are the source of truth.

Base path: `/api/v1/metadata`

## Parse Data Dictionary

`POST /parse/data-dictionary`

Request:

```json
{
  "file_path": "knowledge/Data Dictionary.xlsx"
}
```

Response (shape):

```json
{
  "source": "data_dictionary",
  "file_path": "knowledge/Data Dictionary.xlsx",
  "table_count": 12,
  "column_count": 248,
  "tables": [
    {
      "name": "customer",
      "description": "Customer business entity",
      "columns": [
        {
          "name": "customer_id",
          "data_type": "int",
          "description": "Primary customer key",
          "nullable": false,
          "is_primary_key": false,
          "is_foreign_key": false,
          "references_table": null,
          "source_sheet": "Rich_Data_Dictionary"
        }
      ]
    }
  ]
}
```

## Parse Database Model

`POST /parse/database-model`

Request:

```json
{
  "file_path": "knowledge/Database Model.xlsx"
}
```

Response matches the same canonical metadata structure and sets `source` to `database_model`.

## Build Semantic Relationship Graph

`POST /graphs/semantic`

Request:

```json
{
  "file_path": "knowledge/Data Dictionary.xlsx"
}
```

Response:

```json
{
  "graph_type": "semantic_relationship",
  "node_count": 420,
  "edge_count": 390,
  "nodes": [],
  "edges": []
}
```

## Build Column Lineage Graph

`POST /graphs/lineage`

Request:

```json
{
  "file_path": "knowledge/Data Dictionary.xlsx"
}
```

Response:

```json
{
  "graph_type": "column_lineage",
  "node_count": 420,
  "edge_count": 390,
  "nodes": [],
  "edges": []
}
```

## Build Table Relationship Graph

`POST /graphs/table-relationships`

Request:

```json
{
  "file_path": "knowledge/Database Model.xlsx"
}
```

Response:

```json
{
  "graph_type": "table_relationship",
  "node_count": 37,
  "edge_count": 64,
  "nodes": [],
  "edges": []
}
```

## Generate SQL Automatically

`POST /sql/generate`

Request:

```json
{
  "base_table": "customer",
  "select_columns": ["customer.customer_id", "household.household_id"],
  "filters": {
    "customer.customer_id": 12345
  },
  "limit": 100
}
```

Response:

```json
{
  "sql": "SELECT customer.customer_id, household.household_id FROM customer LEFT JOIN household ON customer.household_id = household.id WHERE customer.customer_id = 12345 LIMIT 100;",
  "joined_tables": ["customer", "household"],
  "unresolved_columns": []
}
```

## Generate Waterfall Analysis Automatically

`POST /waterfall/generate`

Request:

```json
{
  "base_table": "interaction_history",
  "entity_id_column": "customer_id",
  "stages": [
    {
      "name": "contacted",
      "condition": "t.channel = 'email'"
    },
    {
      "name": "responded",
      "condition": "t.response_flag = 1"
    }
  ]
}
```

Response:

```json
{
  "sql": "WITH ...",
  "stage_count": 2,
  "stage_names": ["contacted", "responded"]
}
```

## Generate Explainability Report

`POST /explainability/report`

Request:

```json
{
  "sql": "SELECT customer.customer_id FROM customer LIMIT 100;",
  "semantic_graph": {
    "graph_type": "semantic_relationship",
    "node_count": 2,
    "edge_count": 1,
    "nodes": [],
    "edges": []
  },
  "lineage_graph": {
    "graph_type": "column_lineage",
    "node_count": 2,
    "edge_count": 1,
    "nodes": [],
    "edges": []
  },
  "table_relationship_graph": {
    "graph_type": "table_relationship",
    "node_count": 2,
    "edge_count": 1,
    "nodes": [],
    "edges": []
  }
}
```

Response:

```json
{
  "summary": "Generated SQL is traceable to enterprise metadata through semantic mappings, column lineage links, and table relationships.",
  "assumptions": [
    "Data Dictionary and Database Model workbooks are treated as authoritative metadata sources."
  ],
  "semantic_coverage": {"nodes": 2, "edges": 1},
  "lineage_coverage": {"nodes": 2, "edges": 1},
  "relationship_coverage": {"nodes": 2, "edges": 1},
  "sql_preview": ["SELECT customer.customer_id FROM customer LIMIT 100;"]
}
```
