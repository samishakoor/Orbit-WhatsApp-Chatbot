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
    if not audio_file:
        return "No audio file provided"
    try:
        logger.info(f"Starting transcribing audio file")
        llm = OpenAI()
        transcription = llm.audio.transcriptions.create(
            file=audio_file, model="whisper-1", response_format="text"
        )
        return transcription
    except Exception as e:
        raise ValueError("Error transcribing audio") from e


def transcribe_audio(audio: Audio) -> str:
    logger.info(f"Downloading audio file from Facebook")
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)
    logger.info(f"Downloaded audio file path: {file_path}")
    with open(file_path, "rb") as audio_binary:
        transcription = transcribe_audio_file(audio_binary)
    try:
        os.remove(file_path)
        logger.info(f"Audio file transcribed and deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete audio file: {e}")
    return transcription


def handle_audio_node(state: ChatState) -> ChatState:
    """Node that handles audio messages."""
    logger.info(f"Started processing audio message")
    transcribed_audio_message = transcribe_audio(state.current_message.audio)
    logger.info(
        f"Transcribed Audio Message Received From User: {transcribed_audio_message}"
    )
    if isinstance(transcribed_audio_message, str):
        state.messages.append(HumanMessage(content=transcribed_audio_message))
        return state
    else:
        logger.error(f"❌ Error transcribing audio message: {response}")
        response = "Error transcribing audio message"
    return state
