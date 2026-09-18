from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.models.notification import Notification
from app.models.session import EventSession
from app.models.session_booking import BookingStatus, SessionBooking
from app.models.user import User


class SessionBookingRepository:

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # RELATED ENTITY LOOKUPS
    # ============================================================

    def get_attendee(self, attendee_id: int):
        return self.db.get(Attendee, attendee_id)

    def get_session(self, session_id: int):
        return self.db.get(EventSession, session_id)

    def get_event(self, event_id: int):
        return self.db.get(Event, event_id)

    def get_user(self, user_id: int):
        return self.db.get(User, user_id)

    # ============================================================
    # ACTIVE BOOKING COUNT
    # ============================================================

    def count_active_bookings(self, session_id: int) -> int:
        return (
            self.db.query(func.count(SessionBooking.id))
            .filter(
                SessionBooking.session_id == session_id,
                SessionBooking.status == BookingStatus.BOOKED,
            )
            .scalar()
            or 0
        )

    # ============================================================
    # NOTIFICATION
    # ============================================================

    def create_notification(
        self,
        notification: Notification,
    ):
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    # ============================================================
    # CREATE
    # ============================================================

    def create(
        self,
        booking: SessionBooking,
    ):
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    # ============================================================
    # GET BY ID
    # ============================================================

    def get_by_id(
        self,
        booking_id: int,
    ):
        return (
            self.db.query(SessionBooking)
            .filter(SessionBooking.id == booking_id)
            .first()
        )

    # ============================================================
    # GET ALL
    # ============================================================

    def get_all(self):
        return (
            self.db.query(SessionBooking)
            .order_by(SessionBooking.id)
            .all()
        )

    # ============================================================
    # GET BY ATTENDEE
    # ============================================================

    def get_by_attendee(
        self,
        attendee_id: int,
    ):
        return (
            self.db.query(SessionBooking)
            .filter(
                SessionBooking.attendee_id == attendee_id
            )
            .order_by(SessionBooking.id)
            .all()
        )

    # ============================================================
    # GET BY SESSION
    # ============================================================

    def get_by_session(
        self,
        session_id: int,
    ):
        return (
            self.db.query(SessionBooking)
            .filter(
                SessionBooking.session_id == session_id
            )
            .order_by(SessionBooking.id)
            .all()
        )

    # ============================================================
    # GET EXISTING BOOKING
    # ============================================================

    def get_existing_booking(
        self,
        attendee_id: int,
        session_id: int,
    ):
        return (
            self.db.query(SessionBooking)
            .filter(
                SessionBooking.attendee_id == attendee_id,
                SessionBooking.session_id == session_id,
            )
            .first()
        )

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        booking: SessionBooking,
    ):
        self.db.commit()
        self.db.refresh(booking)
        return booking

    # ============================================================
    # DELETE
    # ============================================================

    def delete(
        self,
        booking: SessionBooking,
    ):
        self.db.delete(booking)
        self.db.commit()