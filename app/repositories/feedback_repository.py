from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_attendee(self, attendee_id: int) -> Attendee | None:
        return self.db.get(Attendee, attendee_id)

    def get_event(self, event_id: int) -> Event | None:
        return self.db.get(Event, event_id)

    def create(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_by_id(self, feedback_id: int) -> Feedback | None:
        return self.db.get(Feedback, feedback_id)

    def get_by_attendee(self, attendee_id: int) -> list[Feedback]:
        statement = (
            select(Feedback)
            .where(Feedback.attendee_id == attendee_id)
            .order_by(Feedback.id)
        )
        return list(self.db.scalars(statement).all())

    def get_by_event(self, event_id: int) -> list[Feedback]:
        statement = (
            select(Feedback)
            .where(Feedback.event_id == event_id)
            .order_by(Feedback.id)
        )
        return list(self.db.scalars(statement).all())

    def get_existing_feedback(
        self,
        attendee_id: int,
        event_id: int,
    ) -> Feedback | None:
        statement = select(Feedback).where(
            Feedback.attendee_id == attendee_id,
            Feedback.event_id == event_id,
        )
        return self.db.scalars(statement).first()

    def get_all(self) -> list[Feedback]:
        statement = select(Feedback).order_by(Feedback.id)
        return list(self.db.scalars(statement).all())

    def update(self, feedback: Feedback) -> Feedback:
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def delete(self, feedback: Feedback) -> None:
        self.db.delete(feedback)
        self.db.commit()