from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.ai.schemas.workflow_states import ChatState
from app.ai.prompts.prompts import SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


def chat_processor_node(state: ChatState) -> ChatState:
    """
    Node that processes chat messages using OpenAI's language model with context limiting.

    This function takes the current chat state, limits the conversation history to prevent
    token overflow and hallucinations, prepares messages with a system prompt, sends them
    to the OpenAI language model for processing, and returns the updated state with the
    AI's response appended to the message history.

    The function automatically limits the context to the last N messages
    to manage token usage and maintain conversation quality.

    Args:
        state (ChatState): The current chat state containing:
            - messages: List of previous chat messages in the conversation
            - Other state properties as defined in ChatState schema

    Returns:
        ChatState: Updated chat state with the AI response appended to messages list

    Raises:
        Exception: If OpenAI API call fails or other processing errors occur

    Note:
        Message history is automatically limited to prevent token overflow and reduce
        hallucinations.The full conversation history is preserved in the state, but only recent
        messages are sent to the LLM for context.
    """
    logger.info(f"[CHAT_PROCESSOR_NODE] Started processing chat message")
    llm = ChatOpenAI(model=settings.OPENAI_MODEL)
    system_message = [SystemMessage(content=(SYSTEM_PROMPT))]

    # Limit conversation history to prevent token overflow and hallucinations
    max_messages = settings.MAX_MESSAGES_IN_CONTEXT
    if len(state.messages) > max_messages:
        # Keep only the last N messages to maintain recent context
        recent_messages = state.messages[-max_messages:]
        logger.info(
            f"[CHAT_PROCESSOR_NODE] Limited message history from {len(state.messages)} to {len(recent_messages)} messages"
        )
    else:
        recent_messages = state.messages
        logger.info(
            f"[CHAT_PROCESSOR_NODE] Using all {len(state.messages)} messages (within limit)"
        )

    input_messages = system_message + recent_messages
    logger.info(
        f"[CHAT_PROCESSOR_NODE] Input message given to LLM: {input_messages[-1].content}"
    )
    response = llm.invoke(input_messages)
    logger.info(f"[CHAT_PROCESSOR_NODE] Response from LLM: {response.content}")

    # Add the AI response to the messages
    state.messages.append(response)
    return state
