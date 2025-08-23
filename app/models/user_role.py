from uuid import UUID
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id: UUID = Column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: UUID = Column(
        PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships with overlaps parameter to handle the many-to-many relationship
    user = relationship(
        "User",
        back_populates="user_roles",
        overlaps="roles,users",  # Overlaps with both User.roles and Role.users
    )
    role = relationship(
        "Role",
        back_populates="user_roles",
        overlaps="roles,users",  # Overlaps with both User.roles and Role.users
    )

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
