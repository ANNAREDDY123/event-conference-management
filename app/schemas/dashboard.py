from datetime import date

from pydantic import BaseModel


# ============================================================
# ADMIN DASHBOARD
# ============================================================

class AdminDashboardResponse(BaseModel):
    total_events: int
    active_events: int
    completed_events: int
    total_attendees: int
    total_registrations: int
    total_tickets_sold: int
    total_revenue: float
    total_refunds: float
    average_event_rating: float


# ============================================================
# ORGANIZER DASHBOARD
# ============================================================

class OrganizerEventAnalytics(BaseModel):
    event_id: int
    event_name: str
    registrations: int
    ticket_sales: int
    revenue: float
    attendance: int
    session_bookings: int


class OrganizerDashboardResponse(BaseModel):
    organizer_id: int
    total_events: int
    events: list[OrganizerEventAnalytics]


class SpeakerPerformanceResponse(BaseModel):
    speaker_id: int
    speaker_name: str
    rating_count: int
    average_rating: float


class SessionPopularityResponse(BaseModel):
    session_id: int
    session_title: str
    booking_count: int


# ============================================================
# LEVEL 15 REPORTS
# ============================================================

class DailyRegistrationReportResponse(BaseModel):
    registration_date: date
    registration_count: int


class EventRevenueReportResponse(BaseModel):
    event_id: int
    event_name: str
    revenue: float


class TicketSalesReportResponse(BaseModel):
    event_id: int
    event_name: str
    ticket_id: int
    ticket_name: str
    tickets_sold: int
    revenue: float


class AttendanceReportResponse(BaseModel):
    event_id: int
    event_name: str
    attendance_count: int


class SpeakerRatingReportResponse(BaseModel):
    event_id: int
    event_name: str
    speaker_id: int
    speaker_name: str
    rating_count: int
    average_rating: float


class SessionPopularityReportResponse(BaseModel):
    event_id: int
    event_name: str
    session_id: int
    session_title: str
    booking_count: int