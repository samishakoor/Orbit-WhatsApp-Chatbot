from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship, validates
import bcrypt
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: str = Column(String(255), unique=True, index=True, nullable=False)
    password: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean(), default=True)

    # Relationships
    # Direct relationship to UserRole (for managing the association)
    user_roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    # Secondary relationship to Role (for easy access to roles)
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        overlaps="user_roles",  # Tell SQLAlchemy this relationship overlaps with user_roles
    )
    
    @validates("password")
    def validate_password(self, key, password):
        """
        Automatically hash password when it's set or updated.
        This ensures passwords are never stored in plain text.
        """
        if password and not password.startswith("$2b$"):  # Check if already hashed
            pwd_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
            return hashed_password.decode("utf-8")
        return password

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain text password against the stored hash.
        """
        password_byte_enc = plain_password.encode("utf-8")
        # Handle both string and bytes for hashed_password
        if isinstance(self.password, str):
            hashed_password = self.password.encode("utf-8")
        else:
            hashed_password = self.password
        return bcrypt.checkpw(
            password=password_byte_enc, hashed_password=hashed_password
        )

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def is_admin(self) -> bool:
        """Check if user is an admin or super admin."""
        return any(role.name in ["ADMIN", "SUPER_ADMIN"] for role in self.roles)

    def is_staff(self) -> bool:
        """Check if user is staff (has STAFF role)."""
        return any(role.name == "STAFF" for role in self.roles)

    def is_super_admin(self) -> bool:
        """Check if user is a super admin."""
        return any(role.name == "SUPER_ADMIN" for role in self.roles)
