import requests
import json
from app.ai.schemas.workflow_states import ChatState
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message_node(state: ChatState) -> ChatState:
    """
    Workflow node that sends the AI response back to WhatsApp.

    This function takes the latest AI-generated message from the chat state and sends
    it as a WhatsApp message to the original sender using Facebook's Graph API.
    The message is sent as a text message with proper WhatsApp formatting.

    Args:
        state (ChatState): Current chat state containing:
            - current_message: Original message with 'from_' field for recipient
            - messages: List where the last message contains the AI response to send

    Returns:
        ChatState: The same chat state (unchanged after sending message)

    Raises:
        Exception: If the WhatsApp API request fails or returns an error response

    Note:
        Uses Facebook Graph API v22.0 with the configured phone number ID and API key
        from settings. The message is sent as type 'text' with preview_url disabled.
    """

    to = state.current_message.from_
    message = state.messages[-1].content

    logger.info(
        f"[SEND_WHATSAPP_MESSAGE_NODE] Sending text message: '{message}' to {to}"
    )

    url = (
        f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
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
        logger.error(f"[SEND_WHATSAPP_MESSAGE_NODE] Error sending message: {e}")
        raise Exception("Failed to send message")
    return state
