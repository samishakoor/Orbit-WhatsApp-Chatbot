import json
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, requests, status
from app.ai.dependencies import ChatServiceDep
from app.core.dependencies import (
    get_conversation_service,
    get_message_sender,
    message_extractor,
)
from app.core.config import settings
from app.schemas.chat import Message, StatusResponse
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def verify_whatsapp(
    hub_mode: str = Query(
        "subscribe", description="The mode of the webhook", alias="hub.mode"
    ),
    hub_challenge: int = Query(
        ..., description="The challenge to verify the webhook", alias="hub.challenge"
    ),
    hub_verify_token: str = Query(
        ..., description="The verification token", alias="hub.verify_token"
    ),
):
    """
    Verify the WhatsApp webhook
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return hub_challenge

    raise HTTPException(status_code=403, detail="Invalid verification token")


@router.post("/", status_code=200, response_model=StatusResponse)
async def receive_whatsapp_message(
    current_sender: Annotated[str, Depends(get_message_sender)],
    message: Annotated[Message, Depends(message_extractor)],
    chat_service: ChatServiceDep,
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
):
    if not current_sender and not message:
        return StatusResponse(status="OK")

    if not current_sender:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    if message:
        logger.info(f"[CHAT_ENDPOINT] Received message from user {current_sender}")

        logger.info(f"[CHAT_ENDPOINT] Message Payload: {message}")

        # Step 1: Get or create conversation through business service
        conversation = conversation_service.get_or_create_conversation(
            sender_id=current_sender,
        )

        # Step 2: Send message through AI service
        await chat_service.send_message(
            message=message,
            thread_id=conversation.thread_id,
        )

        # Step 3: Update conversation metadata
        conversation_service.update_conversation_metadata(
            conversation_id=conversation.id,
            sender_id=current_sender,
            message_count_increment=2,  # User message + AI response
        )

    return StatusResponse(status="OK")
