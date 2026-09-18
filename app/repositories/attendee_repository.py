from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.models.notification import Notification
from app.models.user import User


class AttendeeRepository:

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # ATTENDEE OPERATIONS
    # ============================================================

    def create(self, attendee: Attendee) -> Attendee:
        self.db.add(attendee)
        self.db.commit()
        self.db.refresh(attendee)

        return attendee

    def get_by_id(
        self,
        attendee_id: int,
    ) -> Attendee | None:

        statement = select(Attendee).where(
            Attendee.id == attendee_id
        )

        return self.db.scalar(statement)

    def get_by_user_and_event(
        self,
        user_id: int,
        event_id: int,
    ) -> Attendee | None:

        statement = select(Attendee).where(
            Attendee.user_id == user_id,
            Attendee.event_id == event_id,
        )

        return self.db.scalar(statement)

    def get_by_event(
        self,
        event_id: int,
    ) -> list[Attendee]:

        statement = (
            select(Attendee)
            .where(
                Attendee.event_id == event_id
            )
            .order_by(
                Attendee.registration_date
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_all(self) -> list[Attendee]:

        statement = (
            select(Attendee)
            .order_by(
                Attendee.registration_date
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ============================================================
    # RELATED ENTITY OPERATIONS
    # ============================================================

    def get_user(
        self,
        user_id: int,
    ) -> User | None:

        statement = select(User).where(
            User.id == user_id
        )

        return self.db.scalar(statement)

    def get_event(
        self,
        event_id: int,
    ) -> Event | None:

        statement = select(Event).where(
            Event.id == event_id
        )

        return self.db.scalar(statement)

    # ============================================================
    # NOTIFICATION OPERATIONS
    # ============================================================

    def create_notification(
        self,
        notification: Notification,
    ) -> Notification:

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        attendee: Attendee,
    ) -> Attendee:

        self.db.commit()
        self.db.refresh(attendee)

        return attendee