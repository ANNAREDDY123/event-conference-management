from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.check_in import CheckIn
from app.models.event import Event


class CheckInRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_attendee(self, attendee_id: int) -> Attendee | None:
        return self.db.get(Attendee, attendee_id)

    def get_event(self, event_id: int) -> Event | None:
        return self.db.get(Event, event_id)

    def create(self, check_in: CheckIn) -> CheckIn:
        self.db.add(check_in)
        self.db.commit()
        self.db.refresh(check_in)
        return check_in

    def get_by_id(self, check_in_id: int) -> CheckIn | None:
        return self.db.get(CheckIn, check_in_id)

    def get_by_attendee(self, attendee_id: int) -> list[CheckIn]:
        statement = (
            select(CheckIn)
            .where(CheckIn.attendee_id == attendee_id)
            .order_by(CheckIn.id)
        )
        return list(self.db.scalars(statement).all())

    def get_by_event(self, event_id: int) -> list[CheckIn]:
        statement = (
            select(CheckIn)
            .where(CheckIn.event_id == event_id)
            .order_by(CheckIn.id)
        )
        return list(self.db.scalars(statement).all())

    def get_existing_check_in(
        self,
        attendee_id: int,
        event_id: int,
    ) -> CheckIn | None:
        statement = select(CheckIn).where(
            CheckIn.attendee_id == attendee_id,
            CheckIn.event_id == event_id,
        )
        return self.db.scalars(statement).first()

    def get_all(self) -> list[CheckIn]:
        statement = select(CheckIn).order_by(CheckIn.id)
        return list(self.db.scalars(statement).all())

    def update(self, check_in: CheckIn) -> CheckIn:
        self.db.commit()
        self.db.refresh(check_in)
        return check_in

    def delete(self, check_in: CheckIn) -> None:
        self.db.delete(check_in)
        self.db.commit()