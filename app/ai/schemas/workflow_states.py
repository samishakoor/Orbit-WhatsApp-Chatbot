from typing import Annotated, Sequence
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(BaseModel):
    """
    State schema for chat workflow.

    Follows LangGraph documentation pattern with message history and context.
    Used for conversational chat with persistent message history.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    sender: str
    answer: str