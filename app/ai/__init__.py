"""
AI module for document processing and RAG functionality.

This module provides:
- Document processing workflows (PDF, DOCX, Excel, Text)
- Vector embeddings and storage
- RAG-based chat functionality
- LangGraph workflow management
"""

import logging
from typing import Any, Dict, Optional


class AILogger:
    """
    Enhanced logger for AI module with rich formatting and emojis.

    Provides structured logging with visual indicators for different AI operations.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.module_name = name.split('.')[-1].upper()

    def info(self, message: str, **kwargs):
        """Log info message with green color and checkmark."""
        formatted_msg = f"✅ [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def debug(self, message: str, **kwargs):
        """Log debug message with yellow color and gear emoji."""
        formatted_msg = f"⚙️  [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.debug(formatted_msg)

    def warning(self, message: str, **kwargs):
        """Log warning message with orange color and warning emoji."""
        formatted_msg = f"⚠️  [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.warning(formatted_msg)

    def error(self, message: str, **kwargs):
        """Log error message with red color and error emoji."""
        formatted_msg = f"❌ [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.error(formatted_msg)

    def success(self, message: str, **kwargs):
        """Log success message with green color and celebration emoji."""
        formatted_msg = f"🎉 [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def processing(self, message: str, **kwargs):
        """Log processing message with blue color and processing emoji."""
        formatted_msg = f"🔄 [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def storage(self, message: str, **kwargs):
        """Log storage operation with database emoji."""
        formatted_msg = f"💾 [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def workflow(self, message: str, **kwargs):
        """Log workflow operation with workflow emoji."""
        formatted_msg = f"🔀 [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def ai_operation(self, message: str, **kwargs):
        """Log AI operation with brain emoji."""
        formatted_msg = f"🧠 [{self.module_name}] {message}"
        if kwargs:
            formatted_msg += f" | {self._format_kwargs(kwargs)}"
        self.logger.info(formatted_msg)

    def _format_kwargs(self, kwargs: Dict[str, Any]) -> str:
        """Format keyword arguments for logging."""
        formatted_parts = []
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) > 50:
                value = f"{value[:47]}..."
            formatted_parts.append(
                f"[cyan]{key}[/cyan]=[magenta]{value}[/magenta]")
        return " ".join(formatted_parts)


def get_ai_logger(name: str) -> AILogger:
    """
    Get an enhanced AI logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        AILogger instance with enhanced formatting
    """
    return AILogger(name)


# Export the logger function
__all__ = ["get_ai_logger", "AILogger"]
