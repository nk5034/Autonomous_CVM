# Domain Model (Phase 2)

This document defines the Domain-Driven Design model for CVM Catalyst Phase 2.

## Bounded Contexts

- Campaign Management
- Audience and Experimentation
- Governance and Access Control
- Workflow and Deployment

## Aggregate Roots

- Campaign
- SelectionBriefing
- User
- Workflow

## Entity Relationship Diagram

```mermaid
erDiagram
    SelectionBriefing ||--o| Campaign : supports
    Campaign ||--o{ CampaignConfiguration : has
    Campaign ||--o{ AudienceDefinition : targets
    Campaign ||--o{ TestCase : verifies
    Campaign ||--o{ Simulation : simulates
    Campaign ||--o{ ABTest : experiments
    Campaign ||--o{ Approval : requires
    Campaign ||--o{ Deployment : deploys
    Campaign ||--o{ Workflow : orchestrates

    User ||--o{ Approval : approves
    User ||--o{ AuditLog : acts

    Role }o--o{ Permission : grants
```

## Domain Service Interaction

```mermaid
flowchart LR
    A[CampaignDomainService] --> C[(CampaignRepository)]
    A --> L[(AuditLogRepository)]

    B[ApprovalDomainService] --> D[(ApprovalRepository)]
    B --> L

    E[DeploymentDomainService] --> F[(DeploymentRepository)]
    E --> L

    G[WorkflowDomainService] --> H[(WorkflowRepository)]
    G --> L
```

## Notes

- Business-specific rules are intentionally not embedded at this stage.
- Services coordinate state transitions and auditing only.
- Repository interfaces define persistence ports for infrastructure adapters.
