import json
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, requests
from app.ai.dependencies import ChatServiceDep
from app.core.dependencies import get_conversation_service, get_message_sender, message_extractor
from app.core.config import settings
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


def send_whatsapp_message(to, message, template=True):
    print("Sending WhatsApp message to", to)
    print("Message:", message)
    url = (
        f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer " + settings.WHATSAPP_API_KEY,
        "Content-Type": "application/json",
    }
    if not template:
        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": "hello_world", "language": {"code": "en_US"}},
        }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


# @router.post("/", status_code=200)
# async def receive_whatsapp(request: Request):
#     payload = await request.json()
#     print("📩 Incoming WhatsApp Webhook Payload:", json.dumps(payload, indent=2))

#     # Extract message
#     entry = payload.get("entry", [])[0]
#     changes = entry.get("changes", [])[0]
#     value = changes.get("value", {})
#     messages = value.get("messages", [])

#     if messages:
#         msg = messages[0]
#         from_number = msg["from"]  # sender's phone
#         text = msg.get("text", {}).get("body")
#         print(f"✅ Message received from {from_number}: {text}")
#         thread = threading.Thread(
#             target=send_whatsapp_message,
#             args=(from_number, "Hello Sami, how are you?", False),
#         )
#         thread.daemon = True
#         thread.start()

#     return {"status": "ok"}



@router.post("/", status_code=200)
async def receive_whatsapp(
    sender: Annotated[str, Depends(get_message_sender)],
    sender_message: Annotated[str, Depends(message_extractor)],
    chat_service: ChatServiceDep,
    conversation_service: Annotated[ConversationService, Depends(get_conversation_service)]
):
    print(f"User: {sender}")
    print(f"User message: {sender_message}")
    if not sender and not sender_message:
        return {"status": "ok"}

    if not sender:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if sender_message:
        print(
            f"Received message from user {sender}: ({sender_message})"
        )
    return {"status": "ok"}