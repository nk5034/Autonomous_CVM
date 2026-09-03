#!/usr/bin/env python3
"""
CVM Catalyst V1 - Phase 1 Repository Structure Generator
Creates the complete enterprise project scaffold
"""

import os
from pathlib import Path
from datetime import datetime

# Define project root - go up one level from scripts folder
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def create_directories():
    """Create all project directories"""
    backend_dirs = [
        "backend/src",
        "backend/src/core",
        "backend/src/core/config",
        "backend/src/models",
        "backend/src/schemas",
        "backend/src/services",
        "backend/src/api",
        "backend/src/api/v1",
        "backend/src/api/v1/endpoints",
        "backend/src/workflows",
        "backend/src/workflows/orchestration",
        "backend/src/workflows/agents",
        "backend/src/db",
        "backend/src/db/migrations",
        "backend/src/db/migrations/versions",
        "backend/src/utils",
        "backend/src/utils/logging",
        "backend/src/utils/validation",
        "backend/tests",
        "backend/tests/unit",
        "backend/tests/integration",
        "backend/tests/fixtures",
        "backend/logs",
    ]
    
    frontend_dirs = [
        "frontend/src",
        "frontend/src/app",
        "frontend/src/app/campaigns",
        "frontend/src/app/analytics",
        "frontend/src/app/settings",
        "frontend/src/components",
        "frontend/src/components/common",
        "frontend/src/components/forms",
        "frontend/src/components/layouts",
        "frontend/src/lib",
        "frontend/src/lib/api",
        "frontend/src/lib/utils",
        "frontend/src/styles",
        "frontend/src/hooks",
        "frontend/src/context",
        "frontend/src/types",
        "frontend/public",
        "frontend/__tests__",
        "frontend/__tests__/unit",
        "frontend/__tests__/integration",
    ]
    
    infra_dirs = [
        "infrastructure/docker",
        "infrastructure/kubernetes",
        "infrastructure/scripts",
        "infrastructure/terraform",
        "infrastructure/monitoring",
        "infrastructure/ssl",
    ]
    
    docs_dirs = [
        "docs/architecture",
        "docs/api",
        "docs/guides",
        "docs/deployment",
    ]
    
    for dir_path in backend_dirs + frontend_dirs + infra_dirs + docs_dirs:
        (PROJECT_ROOT / dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories created")

def create_init_files():
    """Create all __init__.py files"""
    init_files = [
        "backend/__init__.py",
        "backend/src/__init__.py",
        "backend/src/core/__init__.py",
        "backend/src/core/config/__init__.py",
        "backend/src/models/__init__.py",
        "backend/src/schemas/__init__.py",
        "backend/src/services/__init__.py",
        "backend/src/api/__init__.py",
        "backend/src/api/v1/__init__.py",
        "backend/src/api/v1/endpoints/__init__.py",
        "backend/src/workflows/__init__.py",
        "backend/src/workflows/orchestration/__init__.py",
        "backend/src/workflows/agents/__init__.py",
        "backend/src/db/__init__.py",
        "backend/src/db/migrations/__init__.py",
        "backend/src/utils/__init__.py",
        "backend/src/utils/logging/__init__.py",
        "backend/src/utils/validation/__init__.py",
        "backend/tests/__init__.py",
        "backend/tests/unit/__init__.py",
        "backend/tests/integration/__init__.py",
    ]
    
    for file_path in init_files:
        (PROJECT_ROOT / file_path).touch(exist_ok=True)
    
    print("✅ All __init__.py files created")

def create_backend_files():
    """Create backend configuration and utility files"""
    
    # main.py
    (PROJECT_ROOT / "backend/src/main.py").write_text('''"""CVM Catalyst V1 - FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config.settings import settings
from src.api.v1 import api_router
from src.utils.logging.logger import configure_logging

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    yield
    print(f"Shutting down {settings.PROJECT_NAME}")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Agentic Campaign Management Platform",
        version=settings.VERSION,
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.PROJECT_NAME}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
''', encoding='utf-8')
    
    # settings.py
    (PROJECT_ROOT / "backend/src/core/config/settings.py").write_text('''"""Application Settings and Configuration"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "CVM Catalyst"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/cvm_catalyst"
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
''', encoding='utf-8')
    
    # database.py
    (PROJECT_ROOT / "backend/src/db/database.py").write_text('''"""Database Configuration and Session Management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
''', encoding='utf-8')
    
    # models/base.py
    (PROJECT_ROOT / "backend/src/models/base.py").write_text('''"""Base Model with Common Fields"""
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
''', encoding='utf-8')
    
    # api/v1/__init__.py
    (PROJECT_ROOT / "backend/src/api/v1/__init__.py").write_text('''"""API V1 Router"""
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/")
async def root():
    return {"message": "CVM Catalyst API v1"}
''', encoding='utf-8')
    
    # utils/logging/logger.py
    (PROJECT_ROOT / "backend/src/utils/logging/logger.py").write_text('''"""Structured Logging Configuration"""
import logging
import json
from datetime import datetime
from src.core.config.settings import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def configure_logging():
    logger = logging.getLogger("cvm_catalyst")
    logger.setLevel(settings.LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
''', encoding='utf-8')
    
    print("✅ Backend files created")

def create_frontend_files():
    """Create frontend configuration files"""
    
    # package.json
    (PROJECT_ROOT / "frontend/package.json").write_text('''{
  "name": "cvm-catalyst-frontend",
  "version": "1.0.0",
  "description": "CVM Catalyst - Agentic Campaign Management Platform",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^14.0.0"
  }
}
''', encoding='utf-8')
    
    # .env.example
    (PROJECT_ROOT / "frontend/.env.example").write_text('''NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=CVM Catalyst
''', encoding='utf-8')
    
    # tsconfig.json
    (PROJECT_ROOT / "frontend/tsconfig.json").write_text('''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
''', encoding='utf-8')
    
    print("✅ Frontend files created")

def create_docker_files():
    """Create Docker configuration files"""
    
    # Dockerfile.backend
    (PROJECT_ROOT / "infrastructure/docker/Dockerfile.backend").write_text('''FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
''', encoding='utf-8')
    
    # Dockerfile.frontend
    (PROJECT_ROOT / "infrastructure/docker/Dockerfile.frontend").write_text('''FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
''', encoding='utf-8')
    
    # docker-compose.yml
    (PROJECT_ROOT / "infrastructure/docker/docker-compose.yml").write_text('''version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: cvm-catalyst-db
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: ${DB_NAME:-cvm_catalyst}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.backend
    container_name: cvm-catalyst-api
    environment:
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-password}@postgres:5432/${DB_NAME:-cvm_catalyst}
      DEBUG: ${DEBUG:-False}
      API_HOST: 0.0.0.0
      API_PORT: 8000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.frontend
    container_name: cvm-catalyst-web
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
''', encoding='utf-8')
    
    print("✅ Docker files created")

def create_environment_files():
    """Create environment variable templates"""
    
    # backend/.env.example
    (PROJECT_ROOT / "backend/.env.example").write_text('''DEBUG=False
PROJECT_NAME=CVM Catalyst
VERSION=1.0.0
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://postgres:password@localhost:5432/cvm_catalyst
DATABASE_ECHO=False
LOG_LEVEL=INFO
LOG_FORMAT=json
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4
''', encoding='utf-8')
    
    # .env.example
    (PROJECT_ROOT / ".env.example").write_text('''DB_USER=postgres
DB_PASSWORD=password
DB_NAME=cvm_catalyst
DB_HOST=localhost
DB_PORT=5432
BACKEND_DEBUG=False
BACKEND_API_HOST=0.0.0.0
BACKEND_API_PORT=8000
FRONTEND_PORT=3000
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4
''', encoding='utf-8')
    
    print("✅ Environment files created")

def create_root_config_files():
    """Create root level configuration files"""
    
    # pyproject.toml
    (PROJECT_ROOT / "pyproject.toml").write_text('''[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "cvm-catalyst"
version = "1.0.0"
description = "Agentic Campaign Management Platform"
requires-python = ">=3.12"

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
''', encoding='utf-8')
    
    # requirements.txt
    (PROJECT_ROOT / "backend/requirements.txt").write_text('''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0
python-dotenv==1.0.0
structlog==23.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
''', encoding='utf-8')
    
    # .gitignore
    (PROJECT_ROOT / ".gitignore").write_text('''__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.venv
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
.env
.env.local
node_modules/
dist/
.next/
out/
logs/
*.log
''', encoding='utf-8')
    
    print("✅ Root configuration files created")

def create_documentation_files():
    """Create documentation files"""
    
    # README.md
    (PROJECT_ROOT / "README.md").write_text('''# CVM Catalyst V1

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
''', encoding='utf-8')
    
    # backend/README.md
    (PROJECT_ROOT / "backend/README.md").write_text('''# Backend - CVM Catalyst

FastAPI backend with LangGraph orchestration and CrewAI agents.

## Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

## Environment

Copy `.env.example` to `.env` and configure.

## Running

```bash
uvicorn src.main:app --reload
```
''', encoding='utf-8')
    
    # frontend/README.md
    (PROJECT_ROOT / "frontend/README.md").write_text('''# Frontend - CVM Catalyst

Next.js 14 frontend for campaign management.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm start
```
''', encoding='utf-8')
    
    # ARCHITECTURE.md
    (PROJECT_ROOT / "docs/ARCHITECTURE.md").write_text('''# CVM Catalyst Architecture

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
''', encoding='utf-8')
    
    print("✅ Documentation files created")

def create_alembic_files():
    """Create Alembic database migration setup"""
    
    # alembic.ini
    (PROJECT_ROOT / "backend/alembic.ini").write_text('''# Alembic configuration file

[alembic]
sqlalchemy.url = postgresql://user:password@localhost:5432/cvm_catalyst
script_location = src/db/migrations
sqlalchemy.track_on = False
''', encoding='utf-8')
    
    # migrations/env.py
    (PROJECT_ROOT / "backend/src/db/migrations/env.py").write_text('''"""Alembic migration environment"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.core.config.settings import settings
from src.db.database import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''', encoding='utf-8')
    
    # .gitkeep for versions
    (PROJECT_ROOT / "backend/src/db/migrations/versions/.gitkeep").touch(exist_ok=True)
    
    # .gitkeep for logs
    (PROJECT_ROOT / "backend/logs/.gitkeep").touch(exist_ok=True)
    
    print("✅ Alembic files created")

def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("🚀 CVM Catalyst V1 - Phase 1 Repository Structure Generator")
    print("="*70)
    print(f"📁 Project Root: {PROJECT_ROOT}\n")
    
    create_directories()
    create_init_files()
    create_backend_files()
    create_frontend_files()
    create_docker_files()
    create_environment_files()
    create_root_config_files()
    create_documentation_files()
    create_alembic_files()
    
    print("\n" + "="*70)
    print("✅ PHASE 1 REPOSITORY STRUCTURE COMPLETE!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Copy environment files:")
    print("      cp .env.example .env")
    print("      cp backend/.env.example backend/.env")
    print("      cp frontend/.env.example frontend/.env")
    print("\n   2. Start services:")
    print("      docker-compose -f infrastructure/docker/docker-compose.yml up -d")
    print("\n   3. Access services:")
    print("      - Frontend: http://localhost:3000")
    print("      - Backend: http://localhost:8000")
    print("      - API Docs: http://localhost:8000/docs")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
