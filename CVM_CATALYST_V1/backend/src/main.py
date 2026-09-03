"""CVM Catalyst V1 - FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config.settings import settings
from src.api.v1 import api_router
from src.utils.logging.logger import configure_logging
from src.workflows.observability.langsmith import get_langsmith_tracker

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    langsmith_tracker = get_langsmith_tracker()
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Artifact persistence backend: {settings.ARTIFACT_PERSISTENCE_BACKEND}")
    print(f"LangSmith tracing enabled: {langsmith_tracker.enabled}")
    yield
    langsmith_tracker.flush()
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
