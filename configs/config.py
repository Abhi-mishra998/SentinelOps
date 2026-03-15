from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

class Settings(BaseSettings):
    # Cluster Config
    CLUSTER_ID: str = "local-dev-cluster"
    CONTROL_PLANE_URL: Optional[str] = None
    
    # DB Config
    DATABASE_URL: str = "postgresql+asyncpg://k8s-agent:password@localhost:5432/sre_agent"
    
    # AI Config
    AI_BACKEND: Literal["ollama", "openai", "anthropic"] = "ollama"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Paths
    PATTERNS_PATH: str = "knowledge/incident_patterns.json"
    PLAYBOOKS_PATH: str = "playbooks/"
    
    # Notifications
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

