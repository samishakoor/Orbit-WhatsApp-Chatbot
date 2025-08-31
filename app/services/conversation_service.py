from datetime import datetime
import logging
from typing import Annotated, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.db.dependencies import get_db
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service for managing conversation business logic and CRUD operations.

    Handles all database operations and business rules for conversations
    while delegating AI processing to the AI module.
    """

    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
    ):
        self.db = db

    def get_or_create_conversation(
        self, sender_id: str, title: Optional[str] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one for the sender.

        Args:
            sender_id: Sender Phone Number
            title: Optional conversation title

        Returns:
            Conversation object with thread_id

        Raises:
            HTTPException: If sender not found or operation fails
        """
        try:
            # Check if sender exists
            if not sender_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sender not found or access denied",
                )

            # Look for active conversation for this sender
            existing_conversation = (
                self.db.query(Conversation)
                .filter(
                    Conversation.sender_id == sender_id,
                    Conversation.is_active == True,
                )
                .first()
            )

            if existing_conversation:
                logger.info(
                    f"[CONVERSATION_SERVICE] Using existing conversation {existing_conversation.id}"
                )
                return existing_conversation

            # Create new conversation with unique thread ID
            conversation = Conversation(
                sender_id=sender_id,
                thread_id=Conversation.generate_thread_id(
                    sender_id
                ),  # Unique thread ID for LangGraph
                title=title or f"Chat - {sender_id}",
                message_count=0,
                last_message_at=datetime.utcnow(),
                is_active=True,
            )

            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            logger.info(
                f"[CONVERSATION_SERVICE] Created new conversation {conversation.id}"
            )

            return conversation

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"[CONVERSATION_SERVICE] Error creating conversation: {str(e)}"
            )
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation",
            )

    def update_conversation_metadata(
        self,
        conversation_id: UUID,
        sender_id: str,
        message_count_increment: int = 2,  # User message + AI response
        update_last_message: bool = True,
    ) -> Conversation:
        """
        Update conversation metadata after message exchange.

        Args:
            conversation_id: Conversation UUID
            sender_id: Sender ID
            message_count_increment: Number to increment message count by
            update_last_message: Whether to update last_message_at timestamp

        Returns:
            Updated conversation object

        Raises:
            HTTPException: If conversation not found or access denied
        """
        # Get conversation directly without passing user object
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Check if sender owns the conversation using sender_id
        if conversation.sender_id != sender_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation",
            )

        # Update metadata
        conversation.message_count += message_count_increment
        if update_last_message:
            conversation.last_message_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(conversation)

        logger.info(
            f"[CONVERSATION_SERVICE] Updated conversation {conversation_id} metadata"
        )
        return conversation

    def get_conversation(
        self,
        conversation_id: UUID,
        sender_id: str,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID with user authorization.

        Args:
            conversation_id: Conversation UUID
            sender_id: Sender ID

        Returns:
            Conversation object if found and accessible, None otherwise

        Raises:
            HTTPException: If user doesn't have permission to access the conversation
        """
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            return None

        # Check if sender owns the conversation
        if conversation.sender_id != sender_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

        return conversation
    
    def deactivate_conversation(
        self,
        conversation_id: UUID,
        sender_id: str,
    ) -> bool:
        """
        Deactivate a conversation (end the chat session).

        Args:
            conversation_id: Conversation UUID
            sender_id: Sender ID

        Returns:
            True if conversation was deactivated, False if not found

        Raises:
            HTTPException: If user doesn't have permission to deactivate the conversation
        """
        conversation = self.get_conversation(conversation_id, sender_id)
        if not conversation:
            return False

        conversation.is_active = False
        self.db.commit()

        logger.info(
            f"[CONVERSATION_SERVICE] Deactivated conversation {conversation_id}")
        return True