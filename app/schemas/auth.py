from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re
from uuid import UUID
from app.models.role import RoleType


class Token(BaseModel):
    access_token: str
    token_type: str
    roles: List[str]


class TokenData(BaseModel):
    sub: str  # This will store the user ID
    exp: int  # This will store the expiration timestamp
    roles: List[str] = []


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    roles: Optional[List[RoleType]] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password meets requirements:
        - Minimum 8 characters
        - At least one letter
        - At least one number  
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError(
                "Password must contain at least one special character")

        return v


class RoleResponse(BaseModel):
    id: UUID
    name: RoleType
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: Token
