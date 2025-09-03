from app.core.config import settings
import requests
import logging

logger = logging.getLogger(__name__)


def download_file_from_facebook(
    file_id: str, file_type: str, mime_type: str
) -> str | None:
    """
    Download a media file from Facebook's servers using WhatsApp API.

    This function performs a two-step process to download media files:
    1. First GET request to retrieve the download URL using the file ID
    2. Second GET request to download the actual file content
    The downloaded file is saved locally with an appropriate file extension.

    Args:
        file_id (str): Facebook media ID for the file to download
        file_type (str): Type of media file ('image', 'audio', etc.)
        mime_type (str): MIME type of the file (e.g., 'image/jpeg', 'audio/ogg')

    Returns:
        str | None: Local file path where the downloaded file was saved,
        or None if the file type is not supported

    Raises:
        ValueError: If either API request fails or returns non-200 status code

    Note:
        Only 'image' and 'audio' file types are currently supported for return.
        The file extension is extracted from the mime_type parameter.
    """
    logger.info(
        f"Downloading file from Facebook with file id: {file_id}, file type: {file_type}, mime type: {mime_type}"
    )
    # First GET request to retrieve the download URL
    url = f"https://graph.facebook.com/v20.0/{file_id}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_API_KEY}"}
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

        logger.error(
            f"Failed to download file from Facebook. Status code: {response.status_code}"
        )
        raise ValueError(
            f"Failed to download file. Status code: {response.status_code}"
        )

    logger.error(
        f"Failed to retrieve download URL. Status code: {response.status_code}"
    )
    raise ValueError(
        f"Failed to retrieve download URL. Status code: {response.status_code}"
    )
