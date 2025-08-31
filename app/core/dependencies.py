from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.core.guards.authorization_guard import AuthGuardDep
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import TokenData
from app.schemas.chat import Audio, Image, Message, Payload
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]


def parse_audio_file(
    message: Annotated[Message, Depends(parse_message)],
) -> Audio | None:
    if message and message.type == "audio":
        return message.audio
    return None


def parse_image_file(
    message: Annotated[Message, Depends(parse_message)],
) -> Image | None:
    if message and message.type == "image":
        return message.image
    return None


def parse_text_message(
    message: Annotated[Message, Depends(parse_message)],
) -> str | None:
    if message and message.type == "text":
        return message.text.body
    return None

def message_extractor(
    text_message: Annotated[str, Depends(parse_text_message)],
    audio: Annotated[Audio, Depends(parse_audio_file)],
    image: Annotated[Image, Depends(parse_image_file)],
):
    # if audio:
    #     return message_service.transcribe_audio(audio)
    # if image:
    #     return message_service.get_base64_image(image)
    if text_message:
        return text_message
    return None


def get_message_sender(
    message: Annotated[Message, Depends(parse_message)],
) -> User | None:
    if not message:
        return None
    return message.from_


def get_conversation_service(
    db: Annotated[Session, Depends(get_db)],
) -> ConversationService:
    return ConversationService(db)


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_guard: AuthGuardDep,
) -> UserService:
    return UserService(db, auth_service, auth_guard)


def verify_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenData:
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


def get_current_user(
    token_data: Annotated[TokenData, Depends(verify_token)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    user = user_service.get_user_by_id(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user
