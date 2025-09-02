import base64
from typing import Annotated, BinaryIO, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from app.schemas.chat import Audio, Image, Message
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import requests
import json
from openai import OpenAI

load_dotenv(override=True)


# Define the state schema
class GraphState(TypedDict):
    """State schema for our workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    current_message: Message
    answer: str


def transcribe_audio_file(audio_file: BinaryIO) -> str:
    if not audio_file:
        return "No audio file provided"
    try:
        llm = OpenAI()
        transcription = llm.audio.transcriptions.create(
            file=audio_file, model="whisper-1", response_format="text"
        )
        return transcription
    except Exception as e:
        raise ValueError("Error transcribing audio") from e


def transcribe_audio(audio: Audio) -> str:
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)
    print(f"Downloaded audio file path: {file_path}")
    print(f"Downloaded audio file to {file_path}")
    with open(file_path, "rb") as audio_binary:
        transcription = transcribe_audio_file(audio_binary)
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete file: {e}")
    return transcription


def get_image(image: Image) -> str:
    image_path = download_file_from_facebook(image.id, "image", image.mime_type)
    print(f"Downloaded image file path: {image_path}")
    with open(image_path, "rb") as image_binary:
        base64_str = base64.b64encode(image_binary.read()).decode("utf-8")
        base64_image = f"data:{image.mime_type};base64,{base64_str}"
    try:
        os.remove(image_path)
    except Exception as e:
        print(f"Failed to delete file: {e}")
    return base64_image


def download_file_from_facebook(
    file_id: str, file_type: str, mime_type: str
) -> str | None:
    # First GET request to retrieve the download URL
    url = f"https://graph.facebook.com/v20.0/{file_id}"
    headers = {"Authorization": f"Bearer {os.getenv('WHATSAPP_API_KEY')}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        download_url = response.json().get("url")

        # Second GET request to download the file
        response = requests.get(download_url, headers=headers)

        if response.status_code == 200:
            file_extension = mime_type.split("/")[-1].split(";")[
                0
            ]  # Extract file extension from mime_type
            file_path = f"{file_id}.{file_extension}"
            with open(file_path, "wb") as file:
                file.write(response.content)
            if file_type == "image" or file_type == "audio":
                return file_path

        raise ValueError(
            f"Failed to download file. Status code: {response.status_code}"
        )
    raise ValueError(
        f"Failed to retrieve download URL. Status code: {response.status_code}"
    )


def handle_image_node(state: GraphState) -> GraphState:
    """Node that handles image messages."""

    print(f"Started handling image message")
    image_data = state["current_message"].image
    image_base64 = get_image(image_data)

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

    state["messages"].append(HumanMessage(content=image_messages))
    return state


def handle_audio_node(state: GraphState) -> GraphState:
    """Node that handles audio messages."""
    print(f"Started transcribing audio message")
    transcribed_audio_message = transcribe_audio(state["current_message"].audio)
    print(f"Transcribed Audio Message: {transcribed_audio_message}")

    if isinstance(transcribed_audio_message, str):
        state["messages"].append(HumanMessage(content=transcribed_audio_message))
        return state
    else:
        print(f"❌ Error transcribing audio message: {response}")
        response = "Error transcribing audio message"
    return state


def handle_text_node(state: GraphState) -> GraphState:
    """Node that handles text messages."""
    print(f"Started handling text message")
    text_message = state["current_message"].text.body
    print(f"💬 Text Message: {text_message}")

    state["messages"].append(HumanMessage(content=text_message))
    return state


def chat_processor_node(state: GraphState) -> GraphState:
    """Node that processes the chat."""
    llm = ChatOpenAI(model="gpt-4o-mini")
    system_message = [
        SystemMessage(
            content=(
                "You are a friendly and helpful WhatsApp assistant. "
                "Users may send you messages in the form of text, images, or audio. "
                "Your job is to understand the input, provide clear and accurate responses, "
                "and communicate naturally in a conversational, WhatsApp-style manner. "
                "Always be polite, approachable, and supportive while assisting the user."
            )
        )
    ]

    messages = system_message + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response], "answer": response.content}


def route_by_message_type(
    state: GraphState,
) -> str:
    """Routes to the appropriate handler based on message type."""
    return state["current_message"].type


def send_whatsapp_message(state: GraphState) -> GraphState:
    """Node that sends a message."""

    to = state["current_message"].from_
    message = state["answer"]

    print(f"Sending message to {to}: {message}")

    url = f"https://graph.facebook.com/v22.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer " + os.getenv("WHATSAPP_API_KEY"),
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
        print(f"❌ Error sending message: {e}")
        raise Exception("Failed to send message")
    return state


def create_workflow() -> StateGraph:
    """Creates and returns the workflow graph."""

    # Create the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("start", lambda state: state)
    workflow.add_node("handle_image", handle_image_node)
    workflow.add_node("handle_audio", handle_audio_node)
    workflow.add_node("handle_text", handle_text_node)
    workflow.add_node("chat_processor", chat_processor_node)
    workflow.add_node("send_message", send_whatsapp_message)

    # Add edges
    workflow.add_edge(START, "start")

    # Conditional edge from start to appropriate handler
    workflow.add_conditional_edges(
        "start",
        route_by_message_type,
        {
            "image": "handle_image",
            "audio": "handle_audio",
            "text": "handle_text",
        },
    )

    workflow.add_edge("handle_text", "chat_processor")
    workflow.add_edge("handle_image", "chat_processor")
    workflow.add_edge("handle_audio", "chat_processor")

    workflow.add_edge("chat_processor", "send_message")
    workflow.add_edge("send_message", END)

    return workflow


def run_example():
    """Runs example conversations through the workflow."""

    # Compile the workflow
    workflow = create_workflow()
    app = workflow.compile()

    print("🚀 Starting LangGraph Workflow with Conditional Edges\n")
    print("=" * 60)

    # Initialize state
    initial_state = GraphState(
        messages=[],
        current_message=Message(
            **{
                "from": "923034835942",
                "id": "wamid.HBgMOTIzMDM0ODM1OTQyFQIAEhggODlGOTM0QzQ0NzQzODkyMzI5NEVBRDMxNEFFQjc2NDMA",
                "timestamp": "1756631116",
                "type": "image",
                "image": {
                    "caption": "Look at this chair",
                    "mime_type": "image/jpeg",
                    "sha256": "k94lPWBwxkS9WRT4eWb4TXldnvdBY5Gk1GHh7Uc+QAQ=",
                    "id": "2498909817131317",
                },
            }
        ),
        answer="",
    )

    # Run the workflow
    try:
        config = {"configurable": {"thread_id": "1"}}
        result = app.invoke(initial_state, config=config)
        print(f"✅ Final Answer: {result['answer']}")
    except Exception as e:
        print(f"❌ Error processing input: {e}")

    print("-" * 40)


if __name__ == "__main__":
    run_example()
