from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.dependencies import (
    get_current_active_user,
    require_roles,
)
from app.utils.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.register_user(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    user, access_token, refresh_token = service.login_user(
        user_data.email,
        user_data.password,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user,
    )


@router.post(
    "/refresh",
)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    access_token = service.refresh_access_token(
        token_data.refresh_token
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    service = AuthService(db)

    return service.deactivate_user(user_id)


@router.patch(
    "/users/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    service = AuthService(db)

    return service.activate_user(user_id)