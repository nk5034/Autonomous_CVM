"""Schemas for enterprise metadata layer APIs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MetadataParseRequest(BaseModel):
    """Optional override for metadata source file path."""

    file_path: str | None = None


class ColumnMetadata(BaseModel):
    """Canonical representation of a column in metadata sources."""

    name: str
    data_type: str | None = None
    description: str | None = None
    nullable: bool | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references_table: str | None = None
    source_sheet: str | None = None


class TableMetadata(BaseModel):
    """Canonical representation of a table in metadata sources."""

    name: str
    description: str | None = None
    columns: list[ColumnMetadata] = Field(default_factory=list)


class ParsedMetadataResponse(BaseModel):
    """Response for parsed metadata from a source workbook."""

    source: str
    file_path: str
    table_count: int
    column_count: int
    tables: list[TableMetadata]


class GraphNode(BaseModel):
    """Graph node in metadata topology representations."""

    id: str
    label: str
    node_type: str
    table: str | None = None
    column: str | None = None


class GraphEdge(BaseModel):
    """Graph edge in metadata topology representations."""

    source: str
    target: str
    relationship_type: str
    confidence: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """Generic graph response for semantic, lineage, and table relationships."""

    graph_type: str
    node_count: int
    edge_count: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class SQLGenerationRequest(BaseModel):
    """Input for automatic SQL generation."""

    base_table: str
    select_columns: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = 100


class SQLGenerationResponse(BaseModel):
    """Generated SQL and traceability details."""

    sql: str
    joined_tables: list[str] = Field(default_factory=list)
    unresolved_columns: list[str] = Field(default_factory=list)


class WaterfallStage(BaseModel):
    """Stage definition for waterfall analysis."""

    name: str
    condition: str


class WaterfallRequest(BaseModel):
    """Input for automatic waterfall query generation."""

    base_table: str
    entity_id_column: str
    stages: list[WaterfallStage] = Field(default_factory=list)


class WaterfallResponse(BaseModel):
    """Generated SQL for a waterfall/funnel analysis."""

    sql: str
    stage_count: int
    stage_names: list[str] = Field(default_factory=list)


class ExplainabilityRequest(BaseModel):
    """Input for explainability report generation."""

    sql: str
    semantic_graph: GraphResponse
    lineage_graph: GraphResponse
    table_relationship_graph: GraphResponse


class ExplainabilityResponse(BaseModel):
    """Explainability report for generated artifacts."""

    summary: str
    assumptions: list[str] = Field(default_factory=list)
    lineage_coverage: dict[str, Any] = Field(default_factory=dict)
    relationship_coverage: dict[str, Any] = Field(default_factory=dict)
    semantic_coverage: dict[str, Any] = Field(default_factory=dict)
