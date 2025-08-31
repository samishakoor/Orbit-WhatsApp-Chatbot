"""
Chat service for AI chat operations and streaming.

This service handles RAG-based chat functionality with conversation
persistence using LangGraph workflows.
"""

from typing import Dict, Any, Optional, AsyncGenerator
from uuid import UUID
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

    async def _get_workflow(self, resource_id: UUID, async_mode: bool = False):
        """
        Get or create RAG chat workflow for the resource.

        Args:
            resource_id: Resource UUID
            async_mode: If True, create async workflow for streaming

        Returns:
            Compiled LangGraph workflow
        """
        try:
            print(
                f"[CHAT_SERVICE] Creating {'async' if async_mode else 'sync'} workflow for resource {resource_id}"
            )

            # Reuse existing checkpointer service (singleton pattern)
            # This prevents creating multiple connection pools
            checkpointer_service = self._checkpointer_service

            # Create workflow with proper async/sync mode
            workflow = await create_chat_workflow(
                resource_id=resource_id,
                checkpointer_service=checkpointer_service,
                async_mode=async_mode,  # Use proper async/sync mode
            )

            print(
                f"[CHAT_SERVICE] Workflow created successfully for resource {resource_id}"
            )
            return workflow

        except Exception as e:
            print(
                f"[CHAT_SERVICE] Failed to create workflow for resource {resource_id}: {str(e)}"
            )
            raise RuntimeError(f"Failed to create workflow: {str(e)}")

    async def send_message(
        self, resource_id: UUID, message: str, thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message and get AI response using RAG workflow.

        Args:
            resource_id: Resource UUID
            message: User message
            thread_id: Optional thread ID for conversation persistence

        Returns:
            AI response with context and sources

        Raises:
            RuntimeError: If processing fails
        """
        try:

            print(
                f"[CHAT_SERVICE] Processing chat message for resource {resource_id}, thread {thread_id}"
            )

            # Prepare workflow input
            input_data = {
                "message": message,
                "resource_id": str(resource_id),
                "thread_id": thread_id or "default",
            }

            # Debug: Log what we're preparing
            print(f"[CHAT_SERVICE] Input data: {input_data}")

            # Validate input
            validated_input = validate_chat_input(input_data)
            config = prepare_chat_config(thread_id or "default")

            # Debug: Log what we're passing to the workflow
            print(f"[CHAT_SERVICE] Validated input: {validated_input}")
            print(f"[CHAT_SERVICE] Config: {config}")

            # Get async workflow for regular chat (consistent with ainvoke)
            workflow = await self._get_workflow(resource_id, async_mode=True)

            # Execute workflow
            print(f"[CHAT_SERVICE] Executing async workflow for resource {resource_id}")
            result = await workflow.ainvoke(validated_input, config=config)
            # Extract response
            answer = result.get("answer", "")
            messages = result.get("messages", [])

            # Get AI message from result
            ai_message = None
            if messages:
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        ai_message = msg
                        break

            if not ai_message:
                ai_message = AIMessage(content=answer)

            print(
                f"[CHAT_SERVICE] Successfully processed message for resource {resource_id}"
            )
            print(f"[CHAT_SERVICE] Generated response length: {len(answer)} characters")

            return {
                "answer": answer,
                "thread_id": thread_id or "default",
                "resource_id": str(resource_id),
            }

        except Exception as e:
            print(
                f"[CHAT_SERVICE] Failed to process chat message for resource {resource_id}: {str(e)}"
            )
            raise RuntimeError(f"Failed to process chat message: {str(e)}")
