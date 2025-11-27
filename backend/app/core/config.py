"""Application Configuration"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    PROJECT_NAME: str = "B2P.AI"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/b2p_ai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - String avec URLs séparées par des virgules
    _BACKEND_CORS_ORIGINS: str = ""

    # Email (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 993
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Email Worker
    EMAIL_CHECK_INTERVAL: int = 5  # Minutes
    DEFAULT_TEAM_ID: str = ""
    DEFAULT_CREATED_BY: str = ""

    # ML Models
    NLP_MODEL_PATH: str = "ml_models/nlp_task_extractor"
    SENTIMENT_MODEL_PATH: str = "ml_models/sentiment_model"
    BURNOUT_MODEL_PATH: str = "ml_models/burnout_predictor"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Google OAuth (for Gmail Sign-In)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""

    # Gemini AI (for Email Extraction)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Fast and cost-effective

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if not self._BACKEND_CORS_ORIGINS:
            return []
        return [i.strip() for i in self._BACKEND_CORS_ORIGINS.split(",") if i.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Ignore les champs extra du .env
    )


# Global settings instance
settings = Settings()
