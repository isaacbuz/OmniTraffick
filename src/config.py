"""Application configuration using Pydantic Settings."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./omnitraffick.db"

    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Celery (Phase 4)
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # External APIs (Phase 4)
    meta_access_token: str | None = None
    meta_ad_account_id: str | None = None
    tiktok_access_token: str | None = None
    google_ads_client_id: str | None = None

    # Vector DB (Phase 6)
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None

    # AI Models (Phase 6)
    openai_api_key: str | None = None
    google_api_key: str | None = None


settings = Settings()
