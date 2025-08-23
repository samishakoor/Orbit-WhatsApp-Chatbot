from functools import wraps
from typing import List, Callable, Any
from fastapi import HTTPException, status
from app.schemas.auth import RoleType
from app.models.user import User


def require_roles(required_roles: List[RoleType]):
    """
    Decorator to enforce role-based access control at the route level.
    This decorator expects the endpoint to have a 'current_user' parameter
    that is injected via FastAPI's dependency injection system.

    Example:
        @router.get("/admin-only")
        @require_roles([RoleType.ADMIN])
        async def admin_route(
            current_user: Annotated[User, Depends(get_current_active_user)]
        ):
            return {"message": "Admin access granted"}

    Args:
        required_roles: List of roles that are allowed to access the route

    Raises:
        HTTPException: If user doesn't have required roles
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Find current_user in the function arguments
            current_user = None

            # Check kwargs first (named parameters)
            if "current_user" in kwargs:
                current_user = kwargs["current_user"]
            else:
                # Check positional arguments (look for User instances)
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Current user not found in function arguments. Ensure 'current_user' parameter is declared.",
                )

            # Check if user has any of the required roles
            user_roles = {role.name for role in current_user.roles}
            if not any(role.value in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required roles: {[role.value for role in required_roles]}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
