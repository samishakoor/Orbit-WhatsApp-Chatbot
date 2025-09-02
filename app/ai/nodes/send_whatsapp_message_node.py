import requests
import json
from app.ai.schemas.workflow_states import ChatState
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message_node(state: ChatState) -> ChatState:
    """Node that sends a message."""

    to = state["current_message"].from_
    message = state["messages"][-1].content

    logger.info(f"Sending text message: '{message}' to {to}")

    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer " + settings.WHATSAPP_API_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "preview_url": False,
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if not response:
            raise Exception("Failed to send message")
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        raise Exception("Failed to send message")
    return state
