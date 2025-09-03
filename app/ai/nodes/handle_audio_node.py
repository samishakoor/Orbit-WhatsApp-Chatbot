import os
from typing import BinaryIO
from langchain_core.messages import HumanMessage
from app.schemas.chat import Audio
from app.ai.schemas.workflow_states import ChatState
from openai import OpenAI
from app.ai.nodes.shared import download_file_from_facebook
import logging

logger = logging.getLogger(__name__)


def transcribe_audio_file(audio_file: BinaryIO) -> str:
    """
    Transcribe an audio file using OpenAI's Whisper model.

    This function takes a binary audio file and uses OpenAI's Whisper-1 model
    to transcribe the audio content into text.

    Args:
        audio_file (BinaryIO): Binary audio file object to be transcribed

    Returns:
        str: Transcribed text from the audio file, or error message if no file provided

    Raises:
        ValueError: If there's an error during the transcription process
    """
    if not audio_file:
        return "No audio file provided"
    try:
        logger.info(f"[HANDLE_AUDIO_NODE] Starting transcribing audio file")
        llm = OpenAI()
        transcription = llm.audio.transcriptions.create(
            file=audio_file, model="whisper-1", response_format="text"
        )
        return transcription
    except Exception as e:
        raise ValueError("Error transcribing audio") from e


def transcribe_audio(audio: Audio) -> str:
    """
    Download and transcribe an audio message from WhatsApp.

    This function downloads an audio file from Facebook's servers using the audio ID,
    transcribes it using OpenAI's Whisper model, and cleans up the temporary file.

    Args:
        audio (Audio): Audio object containing:
            - id: Facebook media ID for the audio file
            - mime_type: MIME type of the audio file

    Returns:
        str: Transcribed text from the audio message

    Raises:
        ValueError: If download or transcription fails
    """
    logger.info(f"[HANDLE_AUDIO_NODE] Downloading audio file from Facebook")
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)
    logger.info(f"[HANDLE_AUDIO_NODE] Downloaded audio file path: {file_path}")
    with open(file_path, "rb") as audio_binary:
        transcription = transcribe_audio_file(audio_binary)
    try:
        os.remove(file_path)
        logger.info(
            f"[HANDLE_AUDIO_NODE] Audio file transcribed and deleted successfully"
        )
    except Exception as e:
        logger.error(f"[HANDLE_AUDIO_NODE] Failed to delete audio file: {e}")
    return transcription


def handle_audio_node(state: ChatState) -> ChatState:
    """
    Workflow node that processes audio messages from WhatsApp.

    This function extracts audio from the current message in the chat state,
    transcribes it to text using OpenAI's Whisper model, and adds the transcribed
    text as a HumanMessage to the conversation history.

    Args:
        state (ChatState): Current chat state containing:
            - current_message: Message object with audio property
            - messages: List of conversation messages to append to

    Returns:
        ChatState: Updated chat state with transcribed audio added as HumanMessage

    Note:
        If transcription fails, an error is logged but the state is still returned
    """
    logger.info(f"[HANDLE_AUDIO_NODE] Started processing audio message")
    transcribed_audio_message = transcribe_audio(state.current_message.audio)
    logger.info(
        f"[HANDLE_AUDIO_NODE] Transcribed Audio Message Received From User: {transcribed_audio_message}"
    )
    if isinstance(transcribed_audio_message, str):
        state.messages.append(HumanMessage(content=transcribed_audio_message))
        return state
    else:
        logger.error(
            f"[HANDLE_AUDIO_NODE] Error transcribing audio message: {response}"
        )
        response = "Error transcribing audio message"
    return state
