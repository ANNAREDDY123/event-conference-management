from fastapi import HTTPException, status

from app.models.attendee import Attendee
from app.models.notification import (
    Notification,
    NotificationType,
)
from app.repositories.attendee_repository import (
    AttendeeRepository,
)
from app.schemas.attendee import (
    AttendeeCreate,
    AttendeeStatusUpdate,
)


class AttendeeService:

    def __init__(self, db):
        self.repository = AttendeeRepository(db)

    # ============================================================
    # REGISTRATION
    # ============================================================

    def register_attendee(
        self,
        attendee_data: AttendeeCreate,
    ) -> Attendee:

        # Check user exists
        user = self.repository.get_user(
            attendee_data.user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check event exists
        event = self.repository.get_event(
            attendee_data.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Check duplicate registration
        existing_attendee = (
            self.repository.get_by_user_and_event(
                attendee_data.user_id,
                attendee_data.event_id,
            )
        )

        if existing_attendee:

            if existing_attendee.status == "Cancelled":
                existing_attendee.status = "Registered"

                attendee = self.repository.update(
                    existing_attendee
                )

                return attendee

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendee is already registered for this event",
            )

        # Check event capacity
        registered_attendees = (
            self.repository.get_by_event(
                attendee_data.event_id
            )
        )

        active_registrations = [
            attendee
            for attendee in registered_attendees
            if attendee.status != "Cancelled"
        ]

        if len(active_registrations) >= event.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event registration capacity is full",
            )

        # Create attendee
        attendee = Attendee(
            user_id=attendee_data.user_id,
            event_id=attendee_data.event_id,
            status="Registered",
        )

        attendee = self.repository.create(
            attendee
        )

        # Registration notification
        notification = Notification(
            user_id=user.id,
            title="Event Registration Successful",
            message=(
                f"You have successfully registered for "
                f"the event '{event.event_name}'."
            ),
            notification_type=NotificationType.REGISTRATION,
        )

        self.repository.create_notification(
            notification
        )

        return attendee

    # ============================================================
    # GET ATTENDEE
    # ============================================================

    def get_attendee(
        self,
        attendee_id: int,
    ) -> Attendee:

        attendee = self.repository.get_by_id(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return attendee

    # ============================================================
    # GET BY EVENT
    # ============================================================

    def get_attendees_by_event(
        self,
        event_id: int,
    ) -> list[Attendee]:

        event = self.repository.get_event(
            event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return self.repository.get_by_event(
            event_id
        )

    # ============================================================
    # GET ALL
    # ============================================================

    def get_attendees(
        self,
    ) -> list[Attendee]:

        return self.repository.get_all()

    # ============================================================
    # CANCEL REGISTRATION
    # ============================================================

    def cancel_registration(
        self,
        attendee_id: int,
    ) -> Attendee:

        attendee = self.repository.get_by_id(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        if attendee.status == "Cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration is already cancelled",
            )

        event = self.repository.get_event(
            attendee.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        attendee.status = "Cancelled"

        attendee = self.repository.update(
            attendee
        )

        # Cancellation notification
        notification = Notification(
            user_id=attendee.user_id,
            title="Event Registration Cancelled",
            message=(
                f"Your registration for the event "
                f"'{event.event_name}' has been cancelled."
            ),
            notification_type=NotificationType.REGISTRATION,
        )

        self.repository.create_notification(
            notification
        )

        return attendee

    # ============================================================
    # UPDATE REGISTRATION STATUS
    # ============================================================

    def update_registration_status(
        self,
        attendee_id: int,
        attendee_data: AttendeeStatusUpdate,
    ) -> Attendee:

        attendee = self.repository.get_by_id(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        allowed_statuses = {
            "Registered",
            "Cancelled",
        }

        if attendee_data.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid attendee status",
            )

        if (
            attendee_data.status == "Cancelled"
            and attendee.status == "Cancelled"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration is already cancelled",
            )

        attendee.status = attendee_data.status

        return self.repository.update(
            attendee
        )