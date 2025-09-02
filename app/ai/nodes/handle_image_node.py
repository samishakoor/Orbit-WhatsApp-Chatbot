import base64
from langchain_core.messages import HumanMessage
from app.schemas.chat import Image
import os
from app.ai.nodes.shared import download_file_from_facebook
from app.ai.schemas.workflow_states import ChatState
import logging

logger = logging.getLogger(__name__)


def get_base64_image(image: Image) -> str:
    logger.info(f"Downloading image file from Facebook")
    image_path = download_file_from_facebook(image.id, "image", image.mime_type)
    logger.info(f"Downloaded image file path: {image_path}")
    with open(image_path, "rb") as image_binary:
        logger.info(f"Starting to convert image file to base64")
        base64_str = base64.b64encode(image_binary.read()).decode("utf-8")
        base64_image = f"data:{image.mime_type};base64,{base64_str}"
        logger.info(f"Image file converted to base64 successfully")
    try:
        os.remove(image_path)
        logger.info(f"Image file processed and deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete image file: {e}")
    return base64_image


def handle_image_node(state: ChatState) -> ChatState:
    """Node that handles image messages."""

    logger.info(f"Started processing image message")
    image_data = state["current_message"].image
    image_base64 = get_base64_image(image_data)

    image_messages = []

    if image_data.caption:
        image_messages.append(
            {
                "type": "text",
                "text": image_data.caption,
            }
        )

    if image_base64:
        image_messages.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_base64,
                },
            }
        )

    logger.info(f"Image Message Received From User: {image_messages}")

    state["messages"].append(HumanMessage(content=image_messages))
    return state
