"""Enterprise metadata layer endpoints (Phase 5)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.security.rbac import require_permissions
from src.schemas.metadata import (
    ExplainabilityRequest,
    ExplainabilityResponse,
    GraphResponse,
    MetadataParseRequest,
    ParsedMetadataResponse,
    SQLGenerationRequest,
    SQLGenerationResponse,
    WaterfallRequest,
    WaterfallResponse,
)
from src.services.metadata_layer import EnterpriseMetadataService

router = APIRouter(prefix="/metadata", tags=["metadata"])
metadata_service = EnterpriseMetadataService()


@router.post("/parse/data-dictionary", response_model=ParsedMetadataResponse)
async def parse_data_dictionary(
    payload: MetadataParseRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> ParsedMetadataResponse:
    parsed = metadata_service.parse_data_dictionary(file_path=payload.file_path)
    return ParsedMetadataResponse.model_validate(parsed)


@router.post("/parse/database-model", response_model=ParsedMetadataResponse)
async def parse_database_model(
    payload: MetadataParseRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> ParsedMetadataResponse:
    parsed = metadata_service.parse_database_model(file_path=payload.file_path)
    return ParsedMetadataResponse.model_validate(parsed)


@router.post("/graphs/semantic", response_model=GraphResponse)
async def semantic_relationship_graph(
    payload: MetadataParseRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> GraphResponse:
    dd = metadata_service.parse_data_dictionary(file_path=payload.file_path)
    db = metadata_service.parse_database_model()
    graph = metadata_service.build_semantic_relationship_graph(dd, db)
    return GraphResponse.model_validate(graph)


@router.post("/graphs/lineage", response_model=GraphResponse)
async def column_lineage_graph(
    payload: MetadataParseRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> GraphResponse:
    dd = metadata_service.parse_data_dictionary(file_path=payload.file_path)
    db = metadata_service.parse_database_model()
    graph = metadata_service.build_column_lineage_graph(dd, db)
    return GraphResponse.model_validate(graph)


@router.post("/graphs/table-relationships", response_model=GraphResponse)
async def table_relationship_graph(
    payload: MetadataParseRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> GraphResponse:
    db = metadata_service.parse_database_model(file_path=payload.file_path)
    graph = metadata_service.build_table_relationship_graph(db)
    return GraphResponse.model_validate(graph)


@router.post("/sql/generate", response_model=SQLGenerationResponse)
async def generate_sql(
    payload: SQLGenerationRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> SQLGenerationResponse:
    db = metadata_service.parse_database_model()
    table_graph = metadata_service.build_table_relationship_graph(db)
    generated = metadata_service.generate_sql(
        base_table=payload.base_table,
        select_columns=payload.select_columns,
        filters=payload.filters,
        table_relationship_graph=table_graph,
        limit=payload.limit,
    )
    return SQLGenerationResponse.model_validate(generated)


@router.post("/waterfall/generate", response_model=WaterfallResponse)
async def generate_waterfall(
    payload: WaterfallRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> WaterfallResponse:
    generated = metadata_service.generate_waterfall_analysis(
        base_table=payload.base_table,
        entity_id_column=payload.entity_id_column,
        stages=[stage.model_dump() for stage in payload.stages],
    )
    return WaterfallResponse.model_validate(generated)


@router.post("/explainability/report", response_model=ExplainabilityResponse)
async def explainability_report(
    payload: ExplainabilityRequest,
    _: object = Depends(require_permissions(["metadata.read"])),
) -> ExplainabilityResponse:
    report = metadata_service.generate_explainability_report(
        sql=payload.sql,
        semantic_graph=payload.semantic_graph.model_dump(),
        lineage_graph=payload.lineage_graph.model_dump(),
        table_relationship_graph=payload.table_relationship_graph.model_dump(),
    )
    return ExplainabilityResponse.model_validate(report)
