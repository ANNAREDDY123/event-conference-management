from datetime import datetime

from fastapi import HTTPException, status

from app.models.event import Event
from app.models.session import EventSession
from app.models.speaker import Speaker
from app.models.venue import Hall
from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionUpdate


class SessionService:
    def __init__(self, db):
        self.repository = SessionRepository(db)

    # ---------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------

    def _get_event(self, event_id: int) -> Event:
        event = self.repository.get_event(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return event

    def _get_speaker(self, speaker_id: int) -> Speaker:
        speaker = self.repository.get_speaker(speaker_id)

        if not speaker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Speaker not found",
            )

        if not speaker.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive speaker cannot be assigned to a session",
            )

        return speaker

    def _get_hall(self, hall_id: int) -> Hall:
        hall = self.repository.get_hall(hall_id)

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall not found",
            )

        return hall

    def _validate_session_times(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> None:

        if end_time <= start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session end time must be after start time",
            )

    def _validate_within_event(
        self,
        event: Event,
        start_time: datetime,
        end_time: datetime,
    ) -> None:

        if start_time < event.start_date or end_time > event.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must be within event start and end time",
            )

    def _validate_capacity(
        self,
        session_capacity: int,
        hall: Hall,
    ) -> None:

        if session_capacity > hall.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session capacity cannot exceed hall capacity",
            )

    def _validate_hall_conflict(
        self,
        hall_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_session_id: int | None = None,
    ) -> None:

        conflicts = self.repository.get_overlapping_hall_sessions(
            hall_id=hall_id,
            start_time=start_time,
            end_time=end_time,
            exclude_session_id=exclude_session_id,
        )

        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hall is already booked for an overlapping session",
            )

    def _validate_speaker_conflict(
        self,
        speaker_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_session_id: int | None = None,
    ) -> None:

        conflicts = self.repository.get_overlapping_speaker_sessions(
            speaker_id=speaker_id,
            start_time=start_time,
            end_time=end_time,
            exclude_session_id=exclude_session_id,
        )

        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Speaker is already assigned to an overlapping session",
            )

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create_session(
        self,
        session_data: SessionCreate,
    ) -> EventSession:

        event = self._get_event(session_data.event_id)

        hall = self._get_hall(session_data.hall_id)

        speaker = None

        if session_data.speaker_id is not None:
            speaker = self._get_speaker(session_data.speaker_id)

        self._validate_session_times(
            session_data.start_time,
            session_data.end_time,
        )

        self._validate_within_event(
            event,
            session_data.start_time,
            session_data.end_time,
        )

        self._validate_capacity(
            session_data.capacity,
            hall,
        )

        self._validate_hall_conflict(
            hall_id=session_data.hall_id,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
        )

        if speaker is not None:
            self._validate_speaker_conflict(
                speaker_id=session_data.speaker_id,
                start_time=session_data.start_time,
                end_time=session_data.end_time,
            )

        new_session = EventSession(
            event_id=session_data.event_id,
            speaker_id=session_data.speaker_id,
            hall_id=session_data.hall_id,
            title=session_data.title,
            description=session_data.description,
            session_type=session_data.session_type,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
            capacity=session_data.capacity,
            status=session_data.status,
        )

        return self.repository.create(new_session)

    # ---------------------------------------------------------
    # Get all
    # ---------------------------------------------------------

    def get_sessions(self) -> list[EventSession]:
        return self.repository.get_all()

    # ---------------------------------------------------------
    # Get by ID
    # ---------------------------------------------------------

    def get_session(
        self,
        session_id: int,
    ) -> EventSession:

        session = self.repository.get_by_id(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return session

    # ---------------------------------------------------------
    # Get sessions by event
    # ---------------------------------------------------------

    def get_sessions_by_event(
        self,
        event_id: int,
    ) -> list[EventSession]:

        self._get_event(event_id)

        return self.repository.get_by_event(event_id)

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update_session(
        self,
        session_id: int,
        session_data: SessionUpdate,
    ) -> EventSession:

        existing_session = self.get_session(session_id)

        update_data = session_data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return existing_session

        event_id = update_data.get(
            "event_id",
            existing_session.event_id,
        )

        hall_id = update_data.get(
            "hall_id",
            existing_session.hall_id,
        )

        speaker_id = update_data.get(
            "speaker_id",
            existing_session.speaker_id,
        )

        start_time = update_data.get(
            "start_time",
            existing_session.start_time,
        )

        end_time = update_data.get(
            "end_time",
            existing_session.end_time,
        )

        capacity = update_data.get(
            "capacity",
            existing_session.capacity,
        )

        event = self._get_event(event_id)

        hall = self._get_hall(hall_id)

        if speaker_id is not None:
            self._get_speaker(speaker_id)

        self._validate_session_times(
            start_time,
            end_time,
        )

        self._validate_within_event(
            event,
            start_time,
            end_time,
        )

        self._validate_capacity(
            capacity,
            hall,
        )

        self._validate_hall_conflict(
            hall_id=hall_id,
            start_time=start_time,
            end_time=end_time,
            exclude_session_id=session_id,
        )

        if speaker_id is not None:
            self._validate_speaker_conflict(
                speaker_id=speaker_id,
                start_time=start_time,
                end_time=end_time,
                exclude_session_id=session_id,
            )

        return self.repository.update(
            existing_session,
            update_data,
        )

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_session(
        self,
        session_id: int,
    ) -> None:

        session = self.get_session(session_id)

        self.repository.delete(session)