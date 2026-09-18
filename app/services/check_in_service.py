from datetime import datetime

from fastapi import HTTPException, status

from app.models.check_in import CheckIn, CheckInStatus
from app.models.event import EventStatus
from app.repositories.check_in_repository import CheckInRepository
from app.schemas.check_in import CheckInCreate, CheckInUpdate


class CheckInService:
    def __init__(self, db):
        self.repository = CheckInRepository(db)

    def create_check_in(self, check_in_data: CheckInCreate) -> CheckIn:
        # Validate attendee
        attendee = self.repository.get_attendee(
            check_in_data.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        # Validate event
        event = self.repository.get_event(
            check_in_data.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Ensure attendee belongs to the event
        if attendee.event_id != event.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendee is not registered for this event",
            )

        # Check event status
        if event.status in {
            EventStatus.CANCELLED,
            EventStatus.COMPLETED,
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-in is not allowed for this event",
            )

        # Prevent duplicate check-in
        existing_check_in = self.repository.get_existing_check_in(
            attendee_id=check_in_data.attendee_id,
            event_id=check_in_data.event_id,
        )

        if existing_check_in:
            if existing_check_in.status == CheckInStatus.CHECKED_IN:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Attendee is already checked in",
                )

            # Allow a previously checked-out attendee to check in again
            existing_check_in.status = CheckInStatus.CHECKED_IN
            existing_check_in.check_in_time = datetime.utcnow()
            existing_check_in.check_out_time = None

            return self.repository.update(existing_check_in)

        # Create new check-in
        check_in = CheckIn(
            attendee_id=check_in_data.attendee_id,
            event_id=check_in_data.event_id,
            check_in_time=datetime.utcnow(),
            status=CheckInStatus.CHECKED_IN,
        )

        return self.repository.create(check_in)

    def get_check_in(self, check_in_id: int) -> CheckIn:
        check_in = self.repository.get_by_id(check_in_id)

        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check-in record not found",
            )

        return check_in

    def get_check_ins(self) -> list[CheckIn]:
        return self.repository.get_all()

    def get_check_ins_by_attendee(
        self,
        attendee_id: int,
    ) -> list[CheckIn]:
        attendee = self.repository.get_attendee(attendee_id)

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return self.repository.get_by_attendee(attendee_id)

    def get_check_ins_by_event(
        self,
        event_id: int,
    ) -> list[CheckIn]:
        event = self.repository.get_event(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return self.repository.get_by_event(event_id)

    def update_check_in(
        self,
        check_in_id: int,
        check_in_data: CheckInUpdate,
    ) -> CheckIn:
        check_in = self.repository.get_by_id(check_in_id)

        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check-in record not found",
            )

        event = self.repository.get_event(check_in.event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        if check_in_data.status == CheckInStatus.CHECKED_OUT:
            if check_in.status == CheckInStatus.CHECKED_OUT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Attendee is already checked out",
                )

            check_in.status = CheckInStatus.CHECKED_OUT
            check_in.check_out_time = datetime.utcnow()

        elif check_in_data.status == CheckInStatus.CHECKED_IN:
            if check_in.status == CheckInStatus.CHECKED_IN:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Attendee is already checked in",
                )

            if event.status in {
                EventStatus.CANCELLED,
                EventStatus.COMPLETED,
            }:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Check-in is not allowed for this event",
                )

            check_in.status = CheckInStatus.CHECKED_IN
            check_in.check_in_time = datetime.utcnow()
            check_in.check_out_time = None

        return self.repository.update(check_in)

    def check_out(self, check_in_id: int) -> CheckIn:
        check_in = self.repository.get_by_id(check_in_id)

        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check-in record not found",
            )

        if check_in.status == CheckInStatus.CHECKED_OUT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendee is already checked out",
            )

        check_in.status = CheckInStatus.CHECKED_OUT
        check_in.check_out_time = datetime.utcnow()

        return self.repository.update(check_in)

    def delete_check_in(self, check_in_id: int) -> None:
        check_in = self.repository.get_by_id(check_in_id)

        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check-in record not found",
            )

        self.repository.delete(check_in)