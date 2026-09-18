from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.check_in import CheckIn, CheckInStatus
from app.models.event import Event, EventStatus
from app.models.feedback import Feedback
from app.models.session import EventSession
from app.models.session_booking import BookingStatus, SessionBooking
from app.models.speaker import Speaker
from app.models.ticket import Ticket
from app.models.ticket_purchase import (
    PaymentStatus,
    PurchaseStatus,
    TicketPurchase,
)


class DashboardRepository:

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # ADMIN DASHBOARD
    # ============================================================

    def get_total_events(self):
        return self.db.query(func.count(Event.id)).scalar() or 0

    def get_active_events(self):
        return (
            self.db.query(func.count(Event.id))
            .filter(
                Event.status.in_(
                    [
                        EventStatus.PUBLISHED,
                        EventStatus.REGISTRATION_OPEN,
                    ]
                )
            )
            .scalar()
            or 0
        )

    def get_completed_events(self):
        return (
            self.db.query(func.count(Event.id))
            .filter(Event.status == EventStatus.COMPLETED)
            .scalar()
            or 0
        )

    def get_total_attendees(self):
        return self.db.query(func.count(Attendee.id)).scalar() or 0

    def get_total_registrations(self):
        return self.db.query(func.count(Attendee.id)).scalar() or 0

    def get_total_tickets_sold(self):
        return (
            self.db.query(
                func.coalesce(func.sum(TicketPurchase.quantity), 0)
            )
            .filter(
                TicketPurchase.payment_status == PaymentStatus.SUCCESS,
                TicketPurchase.purchase_status == PurchaseStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

    def get_total_revenue(self):
        return (
            self.db.query(
                func.coalesce(func.sum(TicketPurchase.total_amount), 0)
            )
            .filter(
                TicketPurchase.payment_status == PaymentStatus.SUCCESS,
                TicketPurchase.purchase_status == PurchaseStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

    def get_total_refunds(self):
        return (
            self.db.query(
                func.coalesce(func.sum(TicketPurchase.total_amount), 0)
            )
            .filter(
                TicketPurchase.payment_status == PaymentStatus.REFUNDED
            )
            .scalar()
            or 0
        )

    def get_average_event_rating(self):
        return (
            self.db.query(
                func.coalesce(func.avg(Feedback.rating), 0)
            )
            .scalar()
            or 0
        )

    # ============================================================
    # ORGANIZER DASHBOARD
    # ============================================================

    def get_organizer_events(self, organizer_id: int):
        return (
            self.db.query(Event)
            .filter(Event.organizer_id == organizer_id)
            .order_by(Event.start_date)
            .all()
        )

    def get_event_registration_count(self, event_id: int):
        return (
            self.db.query(func.count(Attendee.id))
            .filter(Attendee.event_id == event_id)
            .scalar()
            or 0
        )

    def get_event_ticket_sales(self, event_id: int):
        return (
            self.db.query(
                func.coalesce(func.sum(TicketPurchase.quantity), 0)
            )
            .join(
                Ticket,
                Ticket.id == TicketPurchase.ticket_id,
            )
            .filter(
                Ticket.event_id == event_id,
                TicketPurchase.payment_status == PaymentStatus.SUCCESS,
                TicketPurchase.purchase_status == PurchaseStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

    def get_event_revenue(self, event_id: int):
        return (
            self.db.query(
                func.coalesce(func.sum(TicketPurchase.total_amount), 0)
            )
            .join(
                Ticket,
                Ticket.id == TicketPurchase.ticket_id,
            )
            .filter(
                Ticket.event_id == event_id,
                TicketPurchase.payment_status == PaymentStatus.SUCCESS,
                TicketPurchase.purchase_status == PurchaseStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

    def get_event_attendance(self, event_id: int):
        return (
            self.db.query(func.count(CheckIn.id))
            .filter(
                CheckIn.event_id == event_id,
                CheckIn.status.in_(
                    [
                        CheckInStatus.CHECKED_IN,
                        CheckInStatus.CHECKED_OUT,
                    ]
                ),
            )
            .scalar()
            or 0
        )

    def get_event_session_bookings(self, event_id: int):
        return (
            self.db.query(func.count(SessionBooking.id))
            .join(
                EventSession,
                SessionBooking.session_id == EventSession.id,
            )
            .filter(
                EventSession.event_id == event_id,
                SessionBooking.status == BookingStatus.BOOKED,
            )
            .scalar()
            or 0
        )

    # ============================================================
    # ORGANIZER SPEAKER PERFORMANCE
    # ============================================================

    def get_speaker_performance(self, event_id: int):

        event_rating_count = (
            self.db.query(func.count(Feedback.id))
            .filter(Feedback.event_id == event_id)
            .scalar()
            or 0
        )

        event_average_rating = (
            self.db.query(func.coalesce(func.avg(Feedback.rating), 0))
            .filter(Feedback.event_id == event_id)
            .scalar()
            or 0
        )

        rows = (
            self.db.query(
                Speaker.id,
                Speaker.name,
            )
            .join(
                EventSession,
                EventSession.speaker_id == Speaker.id,
            )
            .filter(
                EventSession.event_id == event_id,
                EventSession.speaker_id.isnot(None),
            )
            .distinct()
            .order_by(Speaker.name)
            .all()
        )

        return [
            {
                "id": row.id,
                "name": row.name,
                "rating_count": event_rating_count,
                "average_rating": event_average_rating,
            }
            for row in rows
        ]

    # ============================================================
    # ORGANIZER SESSION POPULARITY
    # ============================================================

    def get_session_popularity(self, event_id: int):

        return (
            self.db.query(
                EventSession.id,
                EventSession.title,
                func.count(SessionBooking.id).label(
                    "booking_count"
                ),
            )
            .outerjoin(
                SessionBooking,
                SessionBooking.session_id == EventSession.id,
            )
            .filter(
                EventSession.event_id == event_id,
                (
                    (SessionBooking.id.is_(None))
                    | (
                        SessionBooking.status
                        == BookingStatus.BOOKED
                    )
                ),
            )
            .group_by(
                EventSession.id,
                EventSession.title,
            )
            .order_by(
                func.count(SessionBooking.id).desc()
            )
            .all()
        )

    # ============================================================
    # LEVEL 15 REPORTS
    # ============================================================

    def get_daily_registrations(
        self,
        event_id: int | None = None,
    ):
        """
        Daily attendee registration count.

        SQLite uses DATE() to group registration_date.
        """

        query = (
            self.db.query(
                func.date(Attendee.registration_date).label(
                    "registration_date"
                ),
                func.count(Attendee.id).label(
                    "registration_count"
                ),
            )
        )

        if event_id is not None:
            query = query.filter(
                Attendee.event_id == event_id
            )

        return (
            query
            .group_by(
                func.date(Attendee.registration_date)
            )
            .order_by(
                func.date(Attendee.registration_date)
            )
            .all()
        )

    def get_event_revenue_report(
        self,
        event_id: int | None = None,
    ):
        query = (
            self.db.query(
                Event.id.label("event_id"),
                Event.event_name.label("event_name"),
                func.coalesce(
                    func.sum(TicketPurchase.total_amount),
                    0,
                ).label("revenue"),
            )
            .outerjoin(
                Ticket,
                Ticket.event_id == Event.id,
            )
            .outerjoin(
                TicketPurchase,
                TicketPurchase.ticket_id == Ticket.id,
            )
            .filter(
                (
                    (TicketPurchase.id.is_(None))
                    | (
                        (
                            TicketPurchase.payment_status
                            == PaymentStatus.SUCCESS
                        )
                        & (
                            TicketPurchase.purchase_status
                            == PurchaseStatus.CONFIRMED
                        )
                    )
                )
            )
        )

        if event_id is not None:
            query = query.filter(Event.id == event_id)

        return (
            query
            .group_by(
                Event.id,
                Event.event_name,
            )
            .order_by(Event.id)
            .all()
        )

    def get_ticket_sales_report(
        self,
        event_id: int | None = None,
    ):
        query = (
            self.db.query(
                Event.id.label("event_id"),
                Event.event_name.label("event_name"),
                Ticket.id.label("ticket_id"),
                Ticket.ticket_name.label("ticket_name"),
                func.coalesce(
                    func.sum(TicketPurchase.quantity),
                    0,
                ).label("tickets_sold"),
                func.coalesce(
                    func.sum(TicketPurchase.total_amount),
                    0,
                ).label("revenue"),
            )
            .join(
                Ticket,
                Ticket.event_id == Event.id,
            )
            .outerjoin(
                TicketPurchase,
                TicketPurchase.ticket_id == Ticket.id,
            )
            .filter(
                (
                    (TicketPurchase.id.is_(None))
                    | (
                        (
                            TicketPurchase.payment_status
                            == PaymentStatus.SUCCESS
                        )
                        & (
                            TicketPurchase.purchase_status
                            == PurchaseStatus.CONFIRMED
                        )
                    )
                )
            )
        )

        if event_id is not None:
            query = query.filter(Event.id == event_id)

        return (
            query
            .group_by(
                Event.id,
                Event.event_name,
                Ticket.id,
                Ticket.ticket_name,
            )
            .order_by(
                Event.id,
                Ticket.id,
            )
            .all()
        )

    def get_attendance_report(
        self,
        event_id: int | None = None,
    ):
        query = (
            self.db.query(
                Event.id.label("event_id"),
                Event.event_name.label("event_name"),
                func.count(CheckIn.id).label(
                    "attendance_count"
                ),
            )
            .outerjoin(
                CheckIn,
                CheckIn.event_id == Event.id,
            )
            .filter(
                (
                    (CheckIn.id.is_(None))
                    | (
                        CheckIn.status.in_(
                            [
                                CheckInStatus.CHECKED_IN,
                                CheckInStatus.CHECKED_OUT,
                            ]
                        )
                    )
                )
            )
        )

        if event_id is not None:
            query = query.filter(Event.id == event_id)

        return (
            query
            .group_by(
                Event.id,
                Event.event_name,
            )
            .order_by(Event.id)
            .all()
        )

    def get_speaker_ratings_report(
        self,
        event_id: int | None = None,
    ):
        """
        Feedback currently belongs to an event, not a speaker.

        Therefore this report returns speakers assigned to
        sessions and the event-level rating information as
        contextual feedback.
        """

        query = (
            self.db.query(
                Event.id.label("event_id"),
                Event.event_name.label("event_name"),
                Speaker.id.label("speaker_id"),
                Speaker.name.label("speaker_name"),
                func.count(
                    func.distinct(Feedback.id)
                ).label("rating_count"),
                func.coalesce(
                    func.avg(Feedback.rating),
                    0,
                ).label("average_rating"),
            )
            .join(
                EventSession,
                EventSession.event_id == Event.id,
            )
            .join(
                Speaker,
                Speaker.id == EventSession.speaker_id,
            )
            .outerjoin(
                Feedback,
                Feedback.event_id == Event.id,
            )
            .filter(
                EventSession.speaker_id.isnot(None)
            )
        )

        if event_id is not None:
            query = query.filter(Event.id == event_id)

        return (
            query
            .group_by(
                Event.id,
                Event.event_name,
                Speaker.id,
                Speaker.name,
            )
            .order_by(
                Event.id,
                Speaker.name,
            )
            .all()
        )

    def get_session_popularity_report(
        self,
        event_id: int | None = None,
    ):
        query = (
            self.db.query(
                Event.id.label("event_id"),
                Event.event_name.label("event_name"),
                EventSession.id.label("session_id"),
                EventSession.title.label("session_title"),
                func.count(
                    SessionBooking.id
                ).label("booking_count"),
            )
            .join(
                EventSession,
                EventSession.event_id == Event.id,
            )
            .outerjoin(
                SessionBooking,
                (
                    (SessionBooking.session_id == EventSession.id)
                    & (
                        SessionBooking.status
                        == BookingStatus.BOOKED
                    )
                ),
            )
        )

        if event_id is not None:
            query = query.filter(Event.id == event_id)

        return (
            query
            .group_by(
                Event.id,
                Event.event_name,
                EventSession.id,
                EventSession.title,
            )
            .order_by(
                Event.id,
                func.count(
                    SessionBooking.id
                ).desc(),
                EventSession.id,
            )
            .all()
        )