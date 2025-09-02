"""
Chat service for AI chat operations and streaming.

This service handles chat functionality with conversation
persistence using LangGraph workflows.
"""

from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.ai.workflows.chat_workflow import (
    create_chat_workflow,
    validate_chat_input,
    prepare_chat_config,
)
import logging
from app.ai.services.checkpointer_service import CheckpointerService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for AI chat operations.

    Handles chat functionality with conversation persistence
    using LangGraph workflows for proper state management.
    """

    def __init__(self):
        """
        Initialize ChatService with required dependencies.
        """

        # Use singleton pattern for checkpointer service
        self._checkpointer_service = CheckpointerService()

    async def _get_workflow(self, async_mode: bool = False):
        """
        Get or create chat workflow.

        Args:
            resource_id: Resource UUID
            async_mode: If True, create async workflow for streaming

        Returns:
            Compiled LangGraph workflow
        """
        try:
            logger.info(
                f"[CHAT_SERVICE] Creating {'async' if async_mode else 'sync'} workflow"
            )

            # Reuse existing checkpointer service (singleton pattern)
            # This prevents creating multiple connection pools
            checkpointer_service = self._checkpointer_service

            # Create workflow with proper async/sync mode
            workflow = await create_chat_workflow(
                checkpointer_service=checkpointer_service,
                async_mode=async_mode,  # Use proper async/sync mode
            )

            logger.info(f"[CHAT_SERVICE] Chat Workflow created successfully")
            return workflow

        except Exception as e:
            logger.error(f"[CHAT_SERVICE] Failed to create chat workflow: {str(e)}")
            raise RuntimeError(f"Failed to create chat workflow: {str(e)}")

    async def send_message(
        self, message: str, thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message and get AI response using RAG workflow.

        Args:
            resource_id: Resource UUID
            sender: sender phone number
            thread_id: Optional thread ID for conversation persistence

        Returns:
            AI response with context and sources

        Raises:
            RuntimeError: If processing fails
        """
        try:

            logger.info(
                f"[CHAT_SERVICE] Processing chat message for thread {thread_id}"
            )

            # Prepare workflow input
            input_data = {
                "message": message,
                "thread_id": thread_id or "default",
            }

            # Debug: Log what we're preparing
            logger.info(f"[CHAT_SERVICE] Input data: {input_data}")

            # Validate input
            validated_input = validate_chat_input(input_data)
            config = prepare_chat_config(thread_id or "default")

            # Debug: Log what we're passing to the workflow
            logger.info(f"[CHAT_SERVICE] Validated input: {validated_input}")
            logger.info(f"[CHAT_SERVICE] Config: {config}")

            # Get async workflow for regular chat (consistent with ainvoke)
            workflow = await self._get_workflow(async_mode=True)

            # Execute workflow
            logger.info(f"[CHAT_SERVICE] Executing async workflow")
            result = await workflow.ainvoke(validated_input, config=config)
            # Extract response
            messages = result.get("messages", [])

            # Get AI message from result
            ai_message = None
            if messages:
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        ai_message = msg.content
                        break

            if not ai_message:
                ai_message = ""

            logger.info(
                f"[CHAT_SERVICE] Successfully processed message"
            )
            logger.info(f"[CHAT_SERVICE] Generated response length: {len(ai_message)} characters")

            return {
                "ai_message": ai_message,
                "thread_id": thread_id or "default",
            }

        except Exception as e:
            logger.error(
                f"[CHAT_SERVICE] Failed to process chat message: {str(e)}"
            )
            raise RuntimeError(f"Failed to process chat message: {str(e)}")
