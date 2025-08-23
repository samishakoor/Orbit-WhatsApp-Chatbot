from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.schemas.auth import RoleResponse, RoleType


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    roles: Optional[List[RoleType]] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class User(UserInDBBase):
    roles: List[RoleResponse] = []


class UserInDB(UserInDBBase):
    hashed_password: str


class UserResponse(User):
    """Response model for user data including roles."""
    pass


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleAssign(BaseModel):
    role_type: str = Field(..., min_length=1, max_length=50)
