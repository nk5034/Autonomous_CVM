# CVM Catalyst Architecture

## Overview

CVM Catalyst is an agentic campaign management platform implementing a multi-stage workflow orchestrated by LangGraph with specialist CrewAI agents.

## Technology Stack

### Backend
- FastAPI 0.104+ (async Python 3.12+)
- LangGraph for workflow orchestration
- CrewAI for specialist agents
- PostgreSQL 16 with SQLAlchemy
- Pydantic v2 for validation
- Structlog for JSON logging

### Frontend
- Next.js 14 with React 18
- TypeScript strict mode
- Zustand for state management
- TailwindCSS for styling

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 16
- Kubernetes ready (future)

## Campaign Flow

1. Briefing Intake
2. Briefing Standardization
3. Briefing Validation
4. Campaign Configuration
5. Scheduling
6. Audience Selection
7. Prioritization
8. Volume Constraints
9. Contact Rules
10. Control Groups
11. Channel Export
12. Deployment

## Core Principles

- Human control at every stage
- All decisions are auditable
- All artifacts are editable by humans
- Manual override support
- Deterministic business rules

## Phase 2 Domain Design

- Detailed DDD domain model: [domain-model](architecture/domain-model.md)
- Includes SQLAlchemy entities, Pydantic schemas, repository interfaces, and domain services.

## API References

- Enterprise Metadata Layer (Phase 5): [enterprise-metadata-layer](api/enterprise-metadata-layer.md)
- Campaign Artifacts (Phase 6): [campaign-artifacts](api/campaign-artifacts.md)
- Workflow Orchestration (Phase 7): [workflows](api/workflows.md)
- Synthetic Data (Phase 8): [synthetic-data](api/synthetic-data.md)
