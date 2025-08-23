from fastapi import Depends
from typing import Annotated
from app.models.user import User
from app.schemas.auth import RoleType


class AuthorizationGuard:
    """
    Guard class responsible for authorization rules and access control.
    This is where all business rules for resource access live.
    """

    def can_access_user(self, current_user: User, target_user: User) -> bool:
        """
        Determine if current_user can access target_user's data.

        Rules:
        1. Users can always access their own data
        2. Admins can access any user's data
        3. Managers can access users in their department (if implemented)
        """
        # Rule 1: Users can always access their own data
        if current_user.id == target_user.id:
            return True

        # Rule 2: Admins can access any user's data
        if current_user.is_admin() or current_user.is_super_admin():
            return True

        return False

    def can_modify_user(self, current_user: User, target_user: User) -> bool:
        """
        Determine if current_user can modify target_user's data.

        Rules:
        1. Users can modify their own data (except roles)
        2. Admins can modify any user's data
        """
        # Rule 1: Users can modify their own data
        if current_user.id == target_user.id:
            return True

        # Rule 2: Admins can modify any user's data
        if current_user.is_admin() or current_user.is_super_admin():
            return True

        return False


def get_authorization_guard() -> AuthorizationGuard:
    """
    Get AuthorizationGuard instance for dependency injection.
    """
    return AuthorizationGuard()


# Dependency alias for dependency injection
AuthGuardDep = Annotated[AuthorizationGuard, Depends(get_authorization_guard)]
