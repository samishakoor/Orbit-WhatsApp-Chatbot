from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.core.guards.authorization_guard import AuthGuardDep
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import TokenData
from app.schemas.chat import Audio, Contact, Image, Message, MessageType, Payload
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]


def message_extractor(
    message: Annotated[Message, Depends(parse_message)],
) -> Message | None:
    if message:
        if (
            message.type == MessageType.TEXT
            or message.type == MessageType.AUDIO
            or message.type == MessageType.IMAGE
        ):
            return message
    return None


def parse_contact(payload: Payload) -> Contact | None:
    if not payload.entry[0].changes[0].value.contacts:
        return None
    return payload.entry[0].changes[0].value.contacts[0]


def get_message_sender(
    contact: Annotated[Contact, Depends(parse_contact)],
) -> str | None:
    if not contact:
        return None
    return contact.wa_id


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
