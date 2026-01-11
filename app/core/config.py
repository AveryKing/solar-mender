from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic Settings.
    Reads from environment variables and .env file.
    """
    # Application
    PROJECT_NAME: str = "Diviora CI/CD Repair Agent"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./local.db"

    # GitHub
    GITHUB_SECRET: str = "placeholder_secret"
    GITHUB_TOKEN: str = "placeholder_token"
    
    # Google Cloud / Vertex AI
    GOOGLE_CLOUD_PROJECT: str = "placeholder_project"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # Cloud Tasks
    CLOUD_TASKS_QUEUE: str = "repair-jobs-queue"
    # The URL of the Cloud Run service to be called by Cloud Tasks
    SERVICE_URL: str = "https://your-service-url.a.run.app"
    
    # Langfuse
    LANGFUSE_PUBLIC_KEY: str = "pk-lf-..."
    LANGFUSE_SECRET_KEY: str = "sk-lf-..."
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Agent Configuration
    AUTO_MERGE_ENABLED: bool = False
    MIN_CONFIDENCE_THRESHOLD: float = 0.7
    PR_DRAFT_BY_DEFAULT: bool = True
    
    # Cost Controls
    DAILY_COST_LIMIT: float = 100.0  # USD per day
    COST_ALERT_THRESHOLD: float = 0.8  # Alert at 80% of limit
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
