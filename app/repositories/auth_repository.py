from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.db.scalar(statement)

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_active_status(
        self,
        user: User,
        is_active: bool,
    ) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user