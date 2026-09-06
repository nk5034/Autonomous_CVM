"""Application Settings and Configuration"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

        PROJECT_NAME: str = "CVM Catalyst"
        VERSION: str = "1.0.0"
        DEBUG: bool = False
        API_HOST: str = "0.0.0.0"
        API_PORT: int = 8000
        ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
        DATABASE_URL: str = "postgresql://postgres:@127.0.0.1:59939/postgres"
        DATABASE_ECHO: bool = False
        LOG_LEVEL: str = "INFO"
        LOG_FORMAT: str = "json"
        OPENAI_API_KEY: str = ""
        OPENAI_MODEL: str = "gpt-4"
        ARTIFACT_PERSISTENCE_BACKEND: str = "file"
        LANGSMITH_TRACING: bool = False
        LANGSMITH_API_KEY: str = ""
        LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
        LANGSMITH_PROJECT: str = "cvm-catalyst"
        LANGSMITH_ENV: str = "dev"
        LANGSMITH_RELEASE: str = "phase12"
        RBAC_ENABLED: bool = True
        RBAC_DEFAULT_ROLE: str = "Developer"
        
    
settings = Settings()