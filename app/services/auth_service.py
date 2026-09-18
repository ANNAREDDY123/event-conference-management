from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import UserRegister
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_refresh_token,
    verify_password,
)


class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)

    def register_user(self, user_data: UserRegister) -> User:
        existing_user = self.repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            is_active=True,
        )

        return self.repository.create(user)

    def login_user(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str, str]:

        user = self.repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token(
            user.id,
            user.role.value,
        )

        refresh_token = create_refresh_token(
            user.id
        )

        return user, access_token, refresh_token

    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> str:

        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if not is_refresh_token(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        return create_access_token(
            user.id,
            user.role.value,
        )

    def get_current_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        return user

    def deactivate_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return self.repository.update_active_status(
            user,
            False,
        )

    def activate_user(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return self.repository.update_active_status(
            user,
            True,
        )