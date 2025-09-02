"""
Chat workflow definition using function-based approach.

This follows the established pattern where workflows are pure functions
that define the graph structure and return compiled applications.
"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.ai.nodes.chat_processor_node import chat_processor_node
from app.ai.services.checkpointer_service import CheckpointerService
from app.ai.schemas.workflow_states import ChatState
from app.ai.nodes.handle_image_node import handle_image_node
from app.ai.nodes.handle_audio_node import handle_audio_node
from app.ai.nodes.handle_text_node import handle_text_node
from app.ai.nodes.send_whatsapp_message_node import send_whatsapp_message_node
from app.schemas.chat import Message

logger = logging.getLogger(__name__)


async def create_chat_workflow(
    checkpointer_service=None,
    async_mode: bool = False,
) -> StateGraph:
    """
    Create RAG chat workflow for resource-specific document querying.

    Uses proper PostgreSQL checkpointer context manager pattern.
    """

    # Create workflow with proper state schema
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("start", lambda state: state)
    workflow.add_node("handle_image", handle_image_node)
    workflow.add_node("handle_audio", handle_audio_node)
    workflow.add_node("handle_text", handle_text_node)
    workflow.add_node("chat_processor", chat_processor_node)
    workflow.add_node("send_message", send_whatsapp_message_node)

    def route_by_message_type(
        state: ChatState,
    ) -> str:
        """Routes to the appropriate handler based on message type."""
        logger.info(
            f"Received {state.current_message.type} from user {state.current_message.from_}"
        )
        return state.current_message.type

    # Conditional edge from start to appropriate handler
    workflow.add_conditional_edges(
        "start",
        route_by_message_type,
        {
            "image": "handle_image",
            "audio": "handle_audio",
            "text": "handle_text",
        },
    )

    # Add edges
    workflow.add_edge(START, "start")
    workflow.add_edge("handle_text", "chat_processor")
    workflow.add_edge("handle_image", "chat_processor")
    workflow.add_edge("handle_audio", "chat_processor")
    workflow.add_edge("chat_processor", "send_message")
    workflow.add_edge("send_message", END)

    # Use provided checkpointer service or create new one
    if checkpointer_service is None:
        checkpointer_service = CheckpointerService()
        logger.info("[CHAT_WORKFLOW] Created new CheckpointerService")
    else:
        logger.info(
            "[CHAT_WORKFLOW] Using provided CheckpointerService with shared connection"
        )

    # Create checkpointer based on mode
    if async_mode:
        logger.info("[CHAT_WORKFLOW] Using async checkpointer for streaming")
    else:
        logger.info("[CHAT_WORKFLOW] Using sync checkpointer for regular execution")

    checkpointer = await checkpointer_service.create_checkpointer(async_mode)

    # Log checkpointer type
    checkpointer_type = checkpointer_service.get_checkpointer_type(checkpointer)
    logger.info(f"[CHAT_WORKFLOW] Using {checkpointer_type} checkpointer")

    # Compile workflow with checkpointer
    # Note: For PostgreSQL checkpointers, LangGraph will handle the context manager
    app = workflow.compile(checkpointer=checkpointer)

    logger.info(f"[CHAT_WORKFLOW] Workflow compiled successfully")

    return app


def validate_chat_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and prepare input for chat workflow.

    This function prepares the input for LangGraph. The checkpointer will automatically
    handle conversation history by appending the current message to existing messages.

    Args:
        input_data: Raw input data

    Returns:
        Validated and formatted state dict

    Raises:
        ValueError: If input validation fails
    """

    # Extract required fields
    message = input_data.get("message", "")
    thread_id = input_data.get("thread_id", "default")

    if not message:
        raise ValueError("Message is required")

    if not message.from_:
        raise ValueError("Sender is required")

    # Prepare state with current message
    state = {
        "current_message": message,
        "messages": [],
    }

    logger.info(
        f"[CHAT_WORKFLOW] Prepared input state with current message for thread_id: {thread_id}"
    )

    return state


def prepare_chat_config(thread_id: str) -> Dict[str, Any]:
    """
    Prepare configuration for RAG chat workflow execution.

    Args:
        thread_id: Thread identifier for conversation persistence

    Returns:
        Configuration dict for workflow execution
    """
    return {"configurable": {"thread_id": thread_id}}
