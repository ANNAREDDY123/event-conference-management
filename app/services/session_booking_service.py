from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.models.notification import Notification, NotificationType
from app.models.session import EventSession, SessionStatus
from app.models.session_booking import BookingStatus, SessionBooking
from app.models.user import User
from app.repositories.session_booking_repository import SessionBookingRepository
from app.schemas.session_booking import (
    SessionBookingCreate,
    SessionBookingUpdate,
)


class SessionBookingService:

    def __init__(self, db: Session):
        self.repository = SessionBookingRepository(db)

    def create_booking(
        self,
        booking_data: SessionBookingCreate,
    ) -> SessionBooking:

        # ---------------------------------------------------------
        # 1. Validate attendee
        # ---------------------------------------------------------
        attendee = self.repository.get_attendee(
            booking_data.attendee_id,
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        # ---------------------------------------------------------
        # 2. Validate session
        # ---------------------------------------------------------
        session = self.repository.get_session(
            booking_data.session_id,
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        # ---------------------------------------------------------
        # 3. Validate attendee belongs to the same event
        # ---------------------------------------------------------
        if attendee.event_id != session.event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendee does not belong to this event",
            )

        # ---------------------------------------------------------
        # 4. Validate session status
        # ---------------------------------------------------------
        if session.status == SessionStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book a cancelled session",
            )

        if session.status == SessionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book a completed session",
            )

        # ---------------------------------------------------------
        # 5. Check existing booking
        # ---------------------------------------------------------
        existing_booking = self.repository.get_existing_booking(
            attendee_id=booking_data.attendee_id,
            session_id=booking_data.session_id,
        )

        if existing_booking:

            # If the previous booking was cancelled, allow the
            # attendee to book the session again.
            if existing_booking.status == BookingStatus.CANCELLED:

                active_booking_count = (
                    self.repository.count_active_bookings(
                        booking_data.session_id,
                    )
                )

                if active_booking_count >= session.capacity:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Session capacity is full",
                    )

                existing_booking.status = BookingStatus.BOOKED
                existing_booking.booking_date = datetime.utcnow()

                booking = self.repository.update(
                    existing_booking
                )

                self._create_booking_notification(
                    attendee=attendee,
                    session=session,
                )

                return booking

            # Active booking already exists.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendee has already booked this session",
            )

        # ---------------------------------------------------------
        # 6. Check session capacity
        # ---------------------------------------------------------
        active_booking_count = (
            self.repository.count_active_bookings(
                booking_data.session_id,
            )
        )

        if active_booking_count >= session.capacity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Session capacity is full",
            )

        # ---------------------------------------------------------
        # 7. Create booking
        # ---------------------------------------------------------
        booking = SessionBooking(
            attendee_id=booking_data.attendee_id,
            session_id=booking_data.session_id,
            booking_date=datetime.utcnow(),
            status=BookingStatus.BOOKED,
        )

        booking = self.repository.create(
            booking
        )

        # ---------------------------------------------------------
        # 8. Create session booking notification
        # ---------------------------------------------------------
        self._create_booking_notification(
            attendee=attendee,
            session=session,
        )

        return booking

    # ============================================================
    # BOOKING NOTIFICATION
    # ============================================================

    def _create_booking_notification(
        self,
        attendee: Attendee,
        session: EventSession,
    ) -> None:

        user = self.repository.get_user(
            attendee.user_id,
        )

        event = self.repository.get_event(
            session.event_id,
        )

        if not user or not event:
            return

        notification = Notification(
            user_id=user.id,
            title="Session Booking Successful",
            message=(
                f"You have successfully booked the session "
                f"'{session.title}' for the event "
                f"'{event.event_name}'."
            ),
            notification_type=NotificationType.SESSION_BOOKING,
        )

        self.repository.create_notification(
            notification
        )

    # ============================================================
    # GET BOOKING
    # ============================================================

    def get_booking(
        self,
        booking_id: int,
    ) -> SessionBooking:

        booking = self.repository.get_by_id(
            booking_id
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session booking not found",
            )

        return booking

    # ============================================================
    # GET ALL BOOKINGS
    # ============================================================

    def get_bookings(self) -> list[SessionBooking]:
        return self.repository.get_all()

    # ============================================================
    # GET BOOKINGS BY ATTENDEE
    # ============================================================

    def get_bookings_by_attendee(
        self,
        attendee_id: int,
    ) -> list[SessionBooking]:

        attendee = self.repository.get_attendee(
            attendee_id,
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return self.repository.get_by_attendee(
            attendee_id
        )

    # ============================================================
    # GET BOOKINGS BY SESSION
    # ============================================================

    def get_bookings_by_session(
        self,
        session_id: int,
    ) -> list[SessionBooking]:

        session = self.repository.get_session(
            session_id,
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return self.repository.get_by_session(
            session_id
        )

    # ============================================================
    # UPDATE BOOKING
    # ============================================================

    def update_booking(
        self,
        booking_id: int,
        booking_data: SessionBookingUpdate,
    ) -> SessionBooking:

        booking = self.repository.get_by_id(
            booking_id
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session booking not found",
            )

        # ---------------------------------------------------------
        # Cancellation handling
        # ---------------------------------------------------------
        if booking_data.status == BookingStatus.CANCELLED:

            if booking.status == BookingStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Booking is already cancelled",
                )

            booking.status = BookingStatus.CANCELLED

            return self.repository.update(
                booking
            )

        # ---------------------------------------------------------
        # Re-book a cancelled booking
        # ---------------------------------------------------------
        if booking_data.status == BookingStatus.BOOKED:

            if booking.status == BookingStatus.BOOKED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Booking is already active",
                )

            session = self.repository.get_session(
                booking.session_id,
            )

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found",
                )

            if session.status == SessionStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book a cancelled session",
                )

            if session.status == SessionStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book a completed session",
                )

            active_booking_count = (
                self.repository.count_active_bookings(
                    booking.session_id,
                )
            )

            if active_booking_count >= session.capacity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Session capacity is full",
                )

            booking.status = BookingStatus.BOOKED
            booking.booking_date = datetime.utcnow()

            booking = self.repository.update(
                booking
            )

            attendee = self.repository.get_attendee(
                booking.attendee_id,
            )

            if attendee:
                self._create_booking_notification(
                    attendee=attendee,
                    session=session,
                )

            return booking

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking status",
        )

    # ============================================================
    # CANCEL BOOKING
    # ============================================================

    def cancel_booking(
        self,
        booking_id: int,
    ) -> SessionBooking:

        booking = self.repository.get_by_id(
            booking_id
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session booking not found",
            )

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )

        booking.status = BookingStatus.CANCELLED

        return self.repository.update(
            booking
        )

    # ============================================================
    # DELETE BOOKING
    # ============================================================

    def delete_booking(
        self,
        booking_id: int,
    ) -> None:

        booking = self.repository.get_by_id(
            booking_id
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session booking not found",
            )

        self.repository.delete(
            booking
        )