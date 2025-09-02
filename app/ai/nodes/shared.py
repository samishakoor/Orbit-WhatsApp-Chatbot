from app.core.config import settings
import requests
import logging

logger = logging.getLogger(__name__)


def download_file_from_facebook(
    file_id: str, file_type: str, mime_type: str
) -> str | None:
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
