from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Orbit WhatsApp Chatbot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A scalable FastAPI backend for WhatsApp Chatbot"

    # API Configuration
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]  # In production, specify actual domains

    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # WhatsApp
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
