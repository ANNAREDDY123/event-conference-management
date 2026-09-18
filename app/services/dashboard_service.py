from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    # ============================================================
    # ADMIN DASHBOARD
    # ============================================================

    def get_admin_dashboard(self):
        return {
            "total_events": self.repository.get_total_events(),
            "active_events": self.repository.get_active_events(),
            "completed_events": self.repository.get_completed_events(),
            "total_attendees": self.repository.get_total_attendees(),
            "total_registrations": self.repository.get_total_registrations(),
            "total_tickets_sold": self.repository.get_total_tickets_sold(),
            "total_revenue": float(
                self.repository.get_total_revenue()
            ),
            "total_refunds": float(
                self.repository.get_total_refunds()
            ),
            "average_event_rating": round(
                float(
                    self.repository.get_average_event_rating()
                ),
                2,
            ),
        }

    # ============================================================
    # ORGANIZER DASHBOARD
    # ============================================================

    def get_organizer_dashboard(self, organizer_id: int):

        events = self.repository.get_organizer_events(
            organizer_id
        )

        event_data = []

        for event in events:
            event_data.append(
                {
                    "event_id": event.id,
                    "event_name": event.event_name,
                    "registrations": (
                        self.repository
                        .get_event_registration_count(event.id)
                    ),
                    "ticket_sales": (
                        self.repository
                        .get_event_ticket_sales(event.id)
                    ),
                    "revenue": float(
                        self.repository
                        .get_event_revenue(event.id)
                    ),
                    "attendance": (
                        self.repository
                        .get_event_attendance(event.id)
                    ),
                    "session_bookings": (
                        self.repository
                        .get_event_session_bookings(event.id)
                    ),
                }
            )

        return {
            "organizer_id": organizer_id,
            "total_events": len(events),
            "events": event_data,
        }

    # ============================================================
    # SPEAKER PERFORMANCE
    # ============================================================

    def get_speaker_performance(
        self,
        event_id: int,
        organizer_id: int,
    ):

        events = self.repository.get_organizer_events(
            organizer_id
        )

        event_ids = {
            event.id
            for event in events
        }

        if event_id not in event_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this event",
            )

        rows = self.repository.get_speaker_performance(
            event_id
        )

        return [
            {
                "speaker_id": row["id"],
                "speaker_name": row["name"],
                "rating_count": row["rating_count"],
                "average_rating": round(
                    float(row["average_rating"]),
                    2,
                ),
            }
            for row in rows
        ]

    # ============================================================
    # SESSION POPULARITY
    # ============================================================

    def get_session_popularity(
        self,
        event_id: int,
        organizer_id: int,
    ):

        events = self.repository.get_organizer_events(
            organizer_id
        )

        event_ids = {
            event.id
            for event in events
        }

        if event_id not in event_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this event",
            )

        rows = self.repository.get_session_popularity(
            event_id
        )

        return [
            {
                "session_id": row.id,
                "session_title": row.title,
                "booking_count": row.booking_count,
            }
            for row in rows
        ]

    # ============================================================
    # LEVEL 15 REPORTS
    # ============================================================

    def get_daily_registrations(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_daily_registrations(
            event_id
        )

        return [
            {
                "registration_date": row.registration_date,
                "registration_count": row.registration_count,
            }
            for row in rows
        ]

    def get_event_revenue_report(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_event_revenue_report(
            event_id
        )

        return [
            {
                "event_id": row.event_id,
                "event_name": row.event_name,
                "revenue": float(row.revenue),
            }
            for row in rows
        ]

    def get_ticket_sales_report(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_ticket_sales_report(
            event_id
        )

        return [
            {
                "event_id": row.event_id,
                "event_name": row.event_name,
                "ticket_id": row.ticket_id,
                "ticket_name": row.ticket_name,
                "tickets_sold": row.tickets_sold,
                "revenue": float(row.revenue),
            }
            for row in rows
        ]

    def get_attendance_report(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_attendance_report(
            event_id
        )

        return [
            {
                "event_id": row.event_id,
                "event_name": row.event_name,
                "attendance_count": row.attendance_count,
            }
            for row in rows
        ]

    def get_speaker_ratings_report(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_speaker_ratings_report(
            event_id
        )

        return [
            {
                "event_id": row.event_id,
                "event_name": row.event_name,
                "speaker_id": row.speaker_id,
                "speaker_name": row.speaker_name,
                "rating_count": row.rating_count,
                "average_rating": round(
                    float(row.average_rating),
                    2,
                ),
            }
            for row in rows
        ]

    def get_session_popularity_report(
        self,
        event_id: int | None = None,
    ):

        rows = self.repository.get_session_popularity_report(
            event_id
        )

        return [
            {
                "event_id": row.event_id,
                "event_name": row.event_name,
                "session_id": row.session_id,
                "session_title": row.session_title,
                "booking_count": row.booking_count,
            }
            for row in rows
        ]