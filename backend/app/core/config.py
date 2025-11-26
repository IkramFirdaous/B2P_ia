"""Application Configuration"""
from typing import List, Union
from pydantic_settings import BaseSettings
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

    # CORS - can be comma-separated string or list
    BACKEND_CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000"

    # Email (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # ML Models
    NLP_MODEL_PATH: str = "ml_models/nlp_task_extractor"
    SENTIMENT_MODEL_PATH: str = "ml_models/sentiment_model"
    BURNOUT_MODEL_PATH: str = "ml_models/burnout_predictor"

    # Gmail API Configuration
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/api/v1/email-extraction/oauth/callback"
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    
    # Email Extraction Settings
    EMAIL_EXTRACTION_BATCH_SIZE: int = 10  # Number of emails to fetch at once
    EMAIL_EXTRACTION_MAX_EMAILS: int = 50  # Maximum emails to process in one request

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["http://localhost:3000"]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
