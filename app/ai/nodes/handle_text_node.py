from langchain_core.messages import HumanMessage
from app.ai.schemas.workflow_states import ChatState
import logging


logger = logging.getLogger(__name__)


def handle_text_node(state: ChatState) -> ChatState:
    """
    Workflow node that processes text messages from WhatsApp.

    This function extracts the text content from the current message in the chat state
    and adds it as a HumanMessage to the conversation history. This is the simplest
    message type handler, dealing with plain text communication.

    Args:
        state (ChatState): Current chat state containing:
            - current_message: Message object with text property containing body
            - messages: List of conversation messages to append to

    Returns:
        ChatState: Updated chat state with text message added as HumanMessage

    Note:
        The text content is extracted from state.current_message.text.body
    """
    logger.info(f"[HANDLE_TEXT_NODE] Started processing text message")
    text_message = state.current_message.text.body
    logger.info(f"[HANDLE_TEXT_NODE] Text Message Received From User: {text_message}")

    state.messages.append(HumanMessage(content=text_message))
    return state
