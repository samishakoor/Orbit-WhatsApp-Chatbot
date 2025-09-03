import base64
from langchain_core.messages import HumanMessage
from app.schemas.chat import Image
import os
from app.ai.nodes.shared import download_file_from_facebook
from app.ai.schemas.workflow_states import ChatState
import logging

logger = logging.getLogger(__name__)


def get_base64_image(image: Image) -> str:
    """
    Download and convert an image from WhatsApp to base64 format.

    This function downloads an image file from Facebook's servers using the image ID,
    converts it to a base64-encoded data URI, and cleans up the temporary file.
    The resulting base64 string includes the proper MIME type prefix for web display.

    Args:
        image (Image): Image object containing:
            - id: Facebook media ID for the image file
            - mime_type: MIME type of the image (e.g., 'image/jpeg', 'image/png')

    Returns:
        str: Base64-encoded data URI string in format 'data:{mime_type};base64,{data}'

    Raises:
        ValueError: If download fails or file processing errors occur
    """
    logger.info(f"[HANDLE_IMAGE_NODE] Downloading image file from Facebook")
    image_path = download_file_from_facebook(image.id, "image", image.mime_type)
    logger.info(f"[HANDLE_IMAGE_NODE] Downloaded image file path: {image_path}")
    with open(image_path, "rb") as image_binary:
        logger.info(f"[HANDLE_IMAGE_NODE] Starting to convert image file to base64")
        base64_str = base64.b64encode(image_binary.read()).decode("utf-8")
        base64_image = f"data:{image.mime_type};base64,{base64_str}"
        logger.info(f"[HANDLE_IMAGE_NODE] Image file converted to base64 successfully")
    try:
        os.remove(image_path)
        logger.info(
            f"[HANDLE_IMAGE_NODE] Image file processed and deleted successfully"
        )
    except Exception as e:
        logger.error(f"[HANDLE_IMAGE_NODE] Failed to delete image file: {e}")
    return base64_image


def handle_image_node(state: ChatState) -> ChatState:
    """
    Workflow node that processes image messages from WhatsApp.

    This function extracts an image from the current message, downloads and converts
    it to base64 format, and creates a properly formatted message for the language model.
    The message can include both the image data and an optional text caption.

    Args:
        state (ChatState): Current chat state containing:
            - current_message: Message object with image property
            - messages: List of conversation messages to append to

    Returns:
        ChatState: Updated chat state with image message added as HumanMessage
        containing structured content with image_url and optional text components

    Note:
        The resulting message format is compatible with OpenAI's vision models
        that can process both text and image content
    """

    logger.info(f"[HANDLE_IMAGE_NODE] Started processing image message")
    image_data = state.current_message.image
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

    logger.info(
        f"[HANDLE_IMAGE_NODE] Image Message Received From User: {image_messages}"
    )

    state.messages.append(HumanMessage(content=image_messages))
    return state
