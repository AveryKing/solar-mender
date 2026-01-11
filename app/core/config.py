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

    # Database
    DATABASE_URL: str

    # GitHub
    GITHUB_SECRET: str
    GITHUB_TOKEN: str
    
    # Google Cloud / Vertex AI
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # Cloud Tasks
    CLOUD_TASKS_QUEUE: str = "repair-jobs-queue"
    # The URL of the Cloud Run service to be called by Cloud Tasks
    SERVICE_URL: str = "https://your-service-url.a.run.app"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
