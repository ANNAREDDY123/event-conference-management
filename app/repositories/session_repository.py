from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.session import EventSession
from app.models.speaker import Speaker
from app.models.venue import Hall


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Session Operations
    # ---------------------------------------------------------

    def create(self, session: EventSession) -> EventSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_by_id(self, session_id: int) -> EventSession | None:
        statement = select(EventSession).where(
            EventSession.id == session_id
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[EventSession]:
        statement = select(EventSession).order_by(
            EventSession.start_time
        )

        return list(self.db.scalars(statement).all())

    def get_by_event(self, event_id: int) -> list[EventSession]:
        statement = (
            select(EventSession)
            .where(EventSession.event_id == event_id)
            .order_by(EventSession.start_time)
        )

        return list(self.db.scalars(statement).all())

    # ---------------------------------------------------------
    # Related Entity Operations
    # ---------------------------------------------------------

    def get_event(self, event_id: int) -> Event | None:
        statement = select(Event).where(
            Event.id == event_id
        )

        return self.db.scalar(statement)

    def get_speaker(self, speaker_id: int) -> Speaker | None:
        statement = select(Speaker).where(
            Speaker.id == speaker_id
        )

        return self.db.scalar(statement)

    def get_hall(self, hall_id: int) -> Hall | None:
        statement = select(Hall).where(
            Hall.id == hall_id
        )

        return self.db.scalar(statement)

    # ---------------------------------------------------------
    # Conflict Checks
    # ---------------------------------------------------------

    def get_overlapping_hall_sessions(
        self,
        hall_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_session_id: int | None = None,
    ) -> list[EventSession]:

        statement = select(EventSession).where(
            EventSession.hall_id == hall_id,
            EventSession.start_time < end_time,
            EventSession.end_time > start_time,
        )

        if exclude_session_id is not None:
            statement = statement.where(
                EventSession.id != exclude_session_id
            )

        return list(self.db.scalars(statement).all())

    def get_overlapping_speaker_sessions(
        self,
        speaker_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_session_id: int | None = None,
    ) -> list[EventSession]:

        statement = select(EventSession).where(
            EventSession.speaker_id == speaker_id,
            EventSession.start_time < end_time,
            EventSession.end_time > start_time,
        )

        if exclude_session_id is not None:
            statement = statement.where(
                EventSession.id != exclude_session_id
            )

        return list(self.db.scalars(statement).all())

    # ---------------------------------------------------------
    # Update / Delete
    # ---------------------------------------------------------

    def update(
        self,
        session: EventSession,
        update_data: dict,
    ) -> EventSession:

        for field, value in update_data.items():
            setattr(session, field, value)

        self.db.commit()
        self.db.refresh(session)

        return session

    def delete(self, session: EventSession) -> None:
        self.db.delete(session)
        self.db.commit()