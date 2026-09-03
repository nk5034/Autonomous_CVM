# Campaign Artifacts API (Phase 6)

Base path: /api/v1/campaign-artifacts

Persistence backend toggle:
- ARTIFACT_PERSISTENCE_BACKEND=file (default): filesystem-backed service
- ARTIFACT_PERSISTENCE_BACKEND=db: SQLAlchemy/Alembic-backed service

Automatic fallback:
- If ARTIFACT_PERSISTENCE_BACKEND=db but DATABASE_URL is not set, endpoints automatically run in file mode.

For db mode, apply migrations first:

alembic upgrade head

## Generate One Artifact

POST /{campaign_id}/generate

Request body:

{
  "artifact_type": "selection_briefing",
  "content": {"objective": "increase retention"},
  "author": "planner.user"
}

Supported artifact_type values:
- selection_briefing
- audience_definition
- campaign_configuration
- proposition_sheet
- treatment_sheet
- contact_rules
- volume_constraints
- control_group_definition
- reporting_configuration

## Generate All Artifacts

POST /{campaign_id}/generate/all

Request body:

{
  "author": "planner.user",
  "content_by_type": {
    "selection_briefing": {"objective": "increase retention"},
    "audience_definition": {"segment": "high_value"}
  }
}

## Versioning

Get full version history for a type:

GET /{campaign_id}/{artifact_type}/versions

Get current active version for a type:

GET /{campaign_id}/{artifact_type}/current

## Approval Workflow

Submit current version for approval:

POST /{campaign_id}/{artifact_type}/approval/submit

Review current pending version:

POST /{campaign_id}/{artifact_type}/approval/review

Request body:

{
  "reviewer": "manager.user",
  "approve": true,
  "comment": "Approved for deployment"
}

## Rollback

Create a new head version from an older version:

POST /{campaign_id}/{artifact_type}/rollback

Request body:

{
  "target_version": 1,
  "actor": "ops.user"
}

## Exports

Export current artifact set to Excel:

POST /{campaign_id}/exports/excel

Export current artifact set to Word:

POST /{campaign_id}/exports/word

Responses include the generated file path.
