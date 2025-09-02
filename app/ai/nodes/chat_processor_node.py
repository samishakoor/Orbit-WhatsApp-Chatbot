from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.ai.schemas.workflow_states import ChatState
import logging

logger = logging.getLogger(__name__)


def chat_processor_node(state: ChatState) -> ChatState:
    """Node that processes the chat."""
    llm = ChatOpenAI(model=settings.OPENAI_MODEL)
    system_message = [
        SystemMessage(
            content=(
                "You are a friendly and helpful WhatsApp assistant. "
                "Users may send you messages in the form of text, images, or audio. "
                "Your job is to understand the input, provide clear and accurate responses, "
                "and communicate naturally in a conversational, WhatsApp-style manner. "
                "Always be polite, approachable, and supportive while assisting the user."
            )
        )
    ]

    messages = system_message + state["messages"]
    logger.info(f"Input message given to LLM: {messages[-1].content}")
    response = llm.invoke(messages)
    logger.info(f"Response from LLM: {response.content}")
    return {"messages": [response]}
