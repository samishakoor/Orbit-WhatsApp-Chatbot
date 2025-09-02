from langchain_core.messages import HumanMessage
from app.ai.schemas.workflow_states import ChatState
import logging


logger = logging.getLogger(__name__)

def handle_text_node(state: ChatState) -> ChatState:
    """Node that handles text messages."""
    logger.info(f"Started processing text message")
    text_message = state.current_message.text.body
    logger.info(f"Text Message Received From User: {text_message}")

    state.messages.append(HumanMessage(content=text_message))
    return state
