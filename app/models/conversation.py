"""
Conversation model for managing chat sessions.

This model stores conversation metadata only. LangGraph's PostgreSQL checkpointer
handles the actual message persistence automatically using thread_id.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime

from app.models.base import BaseModel


class Conversation(BaseModel):
    """
    Conversation model for chat sessions.

    Stores only business metadata - LangGraph handles message persistence
    via PostgreSQL checkpointer using thread_id as the key.
    """

    __tablename__ = "conversations"

    # Core identification
    sender_id = Column(String(255), nullable=False, index=True)

    # LangGraph integration
    thread_id = Column(
        String(255), nullable=False, unique=True, index=True
    )  # LangGraph thread identifier

    # Conversation metadata
    # Auto-generated from first message
    title = Column(String(255), nullable=False)

    # Statistics (for business logic)
    message_count = Column(Integer, default=0)  # Track conversation length
    last_message_at = Column(DateTime, default=datetime.utcnow)  # For sorting/cleanup

    # Status management
    is_active = Column(Boolean, default=True)  # For archiving conversations

    def __repr__(self):
        return f"<Conversation(id={self.id}, thread_id='{self.thread_id}', sender_id={self.sender_id})>"

    @classmethod
    def generate_thread_id(cls, sender_id: str) -> str:
        """
        Generate unique thread ID for LangGraph.

        Format: user_{sender_id}_{timestamp}
        This ensures thread isolation per user.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"user_{sender_id}_{timestamp}"
