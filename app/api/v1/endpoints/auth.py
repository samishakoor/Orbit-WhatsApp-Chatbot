from tokenize import Token
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependencies import get_auth_service, get_user_service
from app.schemas.auth import AuthResponse, UserRegister, UserResponse, Token
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = auth_service.authenticate_user(
        form_data.username, form_data.password
    )  # username field contains email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token with both user object and sub
    access_token = auth_service.create_access_token(
        data={"user": user, "sub": str(user.id)}  # Include the subject (user ID)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "roles": [role.name for role in user.roles],
    }


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    User registration endpoint with optional role assignment
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Create new user
    try:
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            roles=user_data.roles,
        )
        user = user_service.create_user(user_create)

        # Generate token with both user object and sub
        access_token = auth_service.create_access_token(
            data={"user": user, "sub": str(user.id)}  # Include the subject (user ID)
        )

        return AuthResponse(
            message="User registered successfully",
            user=UserResponse.model_validate(user),
            token=Token(
                access_token=access_token,
                token_type="bearer",
                roles=[role.name for role in user.roles],
            ),
        )
    except Exception as e:
        # Log the actual error for debugging (can be removed in production)
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint - for now just returns success
    (In production, you might implement token blacklisting)
    """
    return {"message": "Successfully logged out"}
