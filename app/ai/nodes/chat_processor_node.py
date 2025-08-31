"""
Chat processor node - lightweight container for chat query processing.

This node delegates all chat processing logic to the chat chain.
"""

from typing import Dict, Any
from uuid import UUID
from langchain_core.messages import HumanMessage, AIMessage
from app.ai.schemas.workflow_states import ChatState


def chat_processor_node(state: ChatState) -> Dict[str, Any]:
    """
    Lightweight LangGraph node container for chat processing.

    This node delegates all chat processing logic to the chat chain.

    With RAGChatState and add_messages annotation, LangGraph automatically
    handles conversation history - we just need to return the AI response.

    Args:
        state: RAGChatState containing messages and resource context

    Returns:
        Updated state with chat processing results
    """
    # resource_id = (
    #     state.resource_id
    #     if hasattr(state, "resource_id")
    #     else state.get("resource_id", "unknown")
    # )
    # print(f"[RAG_PROCESSOR_NODE] Starting RAG processing for resource {resource_id}")

    # try:
    #     # Extract messages from state (LangGraph already merged conversation history)
    #     messages = (
    #         state.messages if hasattr(state, "messages") else state.get("messages", [])
    #     )
    #     if not messages:
    #         print(
    #             f"[RAG_PROCESSOR_NODE] No messages provided for resource {resource_id}"
    #         )
    #         return {
    #             "answer": "No message to process",
    #             "messages": [AIMessage(content="No message to process")],
    #         }

    #     # Get the last human message (the current user input)
    #     last_message = messages[-1]
    #     if not isinstance(last_message, HumanMessage):
    #         print(
    #             f"[RAG_PROCESSOR_NODE] Expected human message for resource {resource_id}"
    #         )
    #         return {
    #             "answer": "Expected human message",
    #             "messages": [AIMessage(content="Expected human message")],
    #         }

    #     user_input = last_message.content
    #     print(
    #         f"[RAG_PROCESSOR_NODE] Processing query: {user_input[:50]}... for resource {resource_id}"
    #     )

    #     # Prepare chat history (exclude the current message)
    #     # LangGraph has already provided us with the full conversation history
    #     chat_history = messages[:-1] if len(messages) > 1 else []

    #     # Initialize RAG processing chain
    #     print(f"[RAG_PROCESSOR_NODE] Initializing RAGChain for resource {resource_id}")

    #     # IMPORTANT: Use shared VectorService from the workflow instead of creating new one
    #     # The vector_service should be passed through the workflow state or we need to modify
    #     # the workflow to pass it to the node. For now, we'll create a new one but this
    #     # should be optimized to use the shared instance.
    #     vector_service = VectorService()  # This will use the shared engine

    #     # Create RAG chain with resource context
    #     rag_chain = RAGChain(UUID(resource_id), vector_service)

    #     # Process through chain
    #     print(f"[RAG_PROCESSOR_NODE] Delegating to RAGChain for resource {resource_id}")

    #     # Use invoke method for consistent processing
    #     chain_result = rag_chain.invoke(
    #         {"input": user_input, "chat_history": chat_history}
    #     )

    #     # Extract results
    #     answer = chain_result

    #     # Create AI response message
    #     ai_message = {"role": "assistant", "content": answer}

    #     print(
    #         f"[RAG_PROCESSOR_NODE] RAG processing completed successfully for resource {resource_id}"
    #     )
    #     print(
    #         f"[RAG_PROCESSOR_NODE] Generated response length: {len(answer)} characters"
    #     )

    #     # SIMPLIFIED: With add_messages annotation, we just return the AI message
    #     # LangGraph will automatically append it to the conversation history
    #     return {
    #         # ← add_messages will append this automatically
    #         "messages": [ai_message],
    #         "answer": answer,
    #     }

    # except Exception as e:
    #     print(
    #         f"[RAG_PROCESSOR_NODE] RAG processor node failed for resource {resource_id}: {str(e)}"
    #     )

    #     error_message = AIMessage(
    #         content=f"I apologize, but I encountered an error: {str(e)}"
    #     )

    #     # Even for errors, let add_messages handle history
    #     return {
    #         "error_message": f"RAG processor node failed: {str(e)}",
    #         # ← add_messages will append this automatically
    #         "messages": [error_message],
    #         "answer": str(e),
    #     }
