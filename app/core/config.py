from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import logging
from rich.logging import RichHandler
from rich.theme import Theme
from rich.console import Console


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

    # Log level
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Chat Configuration
    MAX_MESSAGES_IN_CONTEXT: int = int(os.getenv("MAX_MESSAGES_IN_CONTEXT", "10"))

    # WhatsApp
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()


def setup_logging():
    """Configure beautiful colored logging with Rich."""

    # Create custom theme for log levels
    custom_theme = Theme(
        {
            "logging.level.debug": "yellow",
            "logging.level.info": "green",
            "logging.level.warning": "orange3",
            "logging.level.error": "red",
            "logging.level.critical": "bold red",
            "logging.keyword": "cyan",
            "logging.string": "magenta",
            "logging.number": "bright_blue",
        }
    )

    # Create console with custom theme
    console = Console(theme=custom_theme, force_terminal=True)

    # Create Rich handler
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=True,
        enable_link_path=False,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        locals_max_length=10,
        locals_max_string=80,
        keywords=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    )

    # Configure rich handler format
    rich_handler.setFormatter(
        logging.Formatter(fmt="[%(name)s] %(message)s", datefmt="[%X]")
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add rich handler
    root_logger.addHandler(rich_handler)

    # Configure specific loggers with appropriate levels
    loggers_config = {
        # AI module loggers - detailed logging
        "app.ai": logging.INFO,
        "app.ai.services": logging.INFO,
        "app.ai.nodes": logging.INFO,
        "app.ai.workflows": logging.INFO,
        # Core application loggers
        "app.services": logging.INFO,
        "app.api": logging.INFO,
        "app.core": logging.INFO,
        # Third-party libraries - less verbose
        "langchain": logging.WARNING,
        "openai": logging.WARNING,
        "httpx": logging.WARNING,
        "urllib3": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "alembic": logging.INFO,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,  # Reduce HTTP request spam
        "fastapi": logging.INFO,
        # Vector database
        "langchain_postgres": logging.WARNING,
        "psycopg": logging.WARNING,
    }

    # Apply logger configurations
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = True  # Ensure messages propagate to root logger

    # Log the setup completion
    setup_logger = logging.getLogger("app.core.config")
    setup_logger.info("🎨 [bold green]Rich colored logging configured![/bold green]")
    setup_logger.info(f"📊 Log level: [bold cyan]{settings.LOG_LEVEL}[/bold cyan]")
    setup_logger.info(
        f"🔧 Environment: [bold yellow]{settings.ENVIRONMENT}[/bold yellow]"
    )
