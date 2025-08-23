from enum import Enum
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RoleType(str, Enum):
    STAFF = "STAFF"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class Role(BaseModel):
    __tablename__ = "roles"

    name: str = Column(String(50), unique=True, index=True, nullable=False)
    description: str = Column(String(255), nullable=True)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        overlaps="user_roles"
    )

    def __repr__(self):
        return f"<Role {self.name}>" 