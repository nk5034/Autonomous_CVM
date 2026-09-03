# CVM Catalyst V1

Agentic Campaign Management Platform

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose

### Setup

1. Copy environment files
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. Start services
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.yml up -d
   ```

3. Access services
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

- `backend/` - FastAPI backend
- `frontend/` - Next.js frontend
- `infrastructure/` - Docker, K8s, Terraform configs
- `docs/` - Documentation

## Coding Standards

- Python 3.12+ with type hints
- Pydantic for validation
- Async/await patterns
- Structured JSON logging
- Unit tests required

## Documentation

- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Enterprise Metadata Layer API: [docs/api/enterprise-metadata-layer.md](docs/api/enterprise-metadata-layer.md)
- Campaign Artifacts API: [docs/api/campaign-artifacts.md](docs/api/campaign-artifacts.md)
- Synthetic Data API (Phase 8): [docs/api/synthetic-data.md](docs/api/synthetic-data.md)
- Workflow Orchestration API (Phase 7): [docs/api/workflows.md](docs/api/workflows.md)
- LangSmith Observability (Phase 12): [docs/PHASE12_LANGSMITH.md](docs/PHASE12_LANGSMITH.md)
- Enterprise CI/CD (Phase 14): [docs/deployment/PHASE14_ENTERPRISE_CICD.md](docs/deployment/PHASE14_ENTERPRISE_CICD.md)
