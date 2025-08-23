from typing import Annotated, Optional, List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.db.dependencies import get_db
from app.models.role import Role, RoleType
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.guards.authorization_guard import AuthGuardDep
from app.services.auth_service import AuthService


class UserService:
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        auth_service: Annotated[AuthService, Depends()],
        auth_guard: AuthGuardDep,
    ):
        self.db = db
        self.auth_service = auth_service
        self.auth_guard = auth_guard

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, current_user: User, skip: int, limit: int) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: UserCreate) -> User:
        # Password will be automatically hashed by the model's @validates decorator
        db_user = User(
            email=user.email,
            password=user.password,  # Will be automatically hashed
            is_active=user.is_active,
        )

        # Add roles if specified in UserCreate
        if user.roles:
            for role_type in user.roles:
                role = self.db.query(Role).filter(Role.name == role_type).first()
                if role:
                    db_user.roles.append(role)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(
        self, user_id: str, user_update: UserUpdate, current_user: User
    ) -> Optional[User]:

        target_user = self.get_user(user_id, current_user)
        if not target_user:
            return None

        # Check if user has permission to modify the target user
        if not self.auth_guard.can_modify_user(current_user, target_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this user's data",
            )

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(target_user, field, value)

        self.db.commit()
        self.db.refresh(target_user)
        return target_user

    def delete_user(self, user_id: str, current_user: User) -> bool:
        target_user = self.get_user(user_id, current_user)
        if not target_user:
            return False

        self.db.delete(target_user)
        self.db.commit()
        return True

    def get_user(self, user_id: str, current_user: User) -> Optional[User]:
        target_user = self.db.query(User).filter(User.id == user_id).first()
        if not target_user:
            return None

        if not self.auth_guard.can_access_user(current_user, target_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's data",
            )
        return target_user

    def assign_role(
        self, user_id: str, role_type: RoleType, current_user: User
    ) -> Optional[User]:
        if role_type == RoleType.SUPER_ADMIN:
            if not self.auth_service.is_super_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only super admins can assign super admin role",
                )

        target_user = self.get_user(user_id, current_user)
        if not target_user:
            return None

        if self.auth_service.has_role(target_user, role_type):
            raise HTTPException(
                status_code=403, detail=f"User already has role {role_type.value}"
            )

        role = self.db.query(Role).filter(Role.name == role_type).first()
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role {role_type.value} not found"
            )

        if role not in target_user.roles:
            target_user.roles.append(role)
            self.db.commit()
            self.db.refresh(target_user)

        return target_user

    def remove_role(
        self, user_id: str, role_type: RoleType, current_user: User
    ) -> Optional[User]:
        if role_type == RoleType.SUPER_ADMIN:
            if not self.auth_service.is_super_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only super admins can remove super admin role",
                )

        target_user = self.get_user(user_id, current_user)
        if not target_user:
            return None

        role = self.db.query(Role).filter(Role.name == role_type).first()
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role {role_type.value} not found"
            )

        if not self.auth_service.has_role(target_user, role_type):
            raise HTTPException(
                status_code=403, detail=f"User does not have role {role_type.value}"
            )

        if role in target_user.roles:
            target_user.roles.remove(role)
            self.db.commit()
            self.db.refresh(target_user)

        return target_user

    def get_user_roles(self, user_id: str, current_user: User) -> List[Role]:
        target_user = self.get_user(user_id, current_user)
        if not target_user:
            return []
        return target_user.roles