from typing import List
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.role_decorator import require_roles
from app.models.role import RoleType
from app.models.user import User as UserModel
from app.core.dependencies import get_current_active_user, get_user_service
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/", response_model=List[UserResponse])
@require_roles([RoleType.ADMIN, RoleType.SUPER_ADMIN])
async def get_all_users(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponse]:
    users = user_service.get_users(current_user, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
@require_roles([RoleType.ADMIN, RoleType.SUPER_ADMIN])
async def get_user(
    user_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = user_service.get_user(str(user_id), current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
@require_roles([RoleType.ADMIN, RoleType.SUPER_ADMIN])
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    updated_user = user_service.update_user(
        user_id=str(user_id), user_update=user_update, current_user=current_user
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles([RoleType.ADMIN, RoleType.SUPER_ADMIN])
async def delete_user(
    user_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    if not user_service.delete_user(str(user_id), current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )