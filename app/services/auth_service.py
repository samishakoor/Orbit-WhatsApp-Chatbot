from datetime import timedelta, datetime
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.dependencies import get_db
from jose import JWTError, jwt
from app.core.config import settings
from app.models.role import RoleType
from app.models.user import User
from app.schemas.auth import TokenData


class AuthService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Ensure we have both user object and sub
        user = data.get("user")
        sub = data.get("sub")
        if not user or not sub:
            raise ValueError("Token data must contain both user object and sub")

        # Set up the token payload
        to_encode = {
            "sub": sub,  # Use the provided subject
            "exp": int(expire.timestamp()),  # Store expiration as timestamp
        }

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            token_data = TokenData(**payload)
            return token_data
        except JWTError:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not user.verify_password(password):
            return None
        return user

    def has_role(self, user: User, role: RoleType) -> bool:
        return user.has_role(role)

    def is_admin(self, user: User) -> bool:
        return user.is_admin()

    def is_super_admin(self, user: User) -> bool:
        return user.is_super_admin()
