from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import (
    AdminDashboardResponse,
    AttendanceReportResponse,
    DailyRegistrationReportResponse,
    EventRevenueReportResponse,
    OrganizerDashboardResponse,
    SessionPopularityReportResponse,
    SessionPopularityResponse,
    SpeakerPerformanceResponse,
    SpeakerRatingReportResponse,
    TicketSalesReportResponse,
)
from app.services.dashboard_service import DashboardService
from app.utils.dependencies import require_roles


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
)
def get_admin_dashboard(
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_admin_dashboard()


# ============================================================
# ORGANIZER DASHBOARD
# ============================================================

@router.get(
    "/organizer",
    response_model=OrganizerDashboardResponse,
)
def get_organizer_dashboard(
    current_user=Depends(
        require_roles("Event Organizer")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_organizer_dashboard(
        current_user.id
    )


@router.get(
    "/organizer/{event_id}/speaker-performance",
    response_model=list[SpeakerPerformanceResponse],
)
def get_speaker_performance(
    event_id: int,
    current_user=Depends(
        require_roles("Event Organizer")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_speaker_performance(
        event_id=event_id,
        organizer_id=current_user.id,
    )


@router.get(
    "/organizer/{event_id}/session-popularity",
    response_model=list[SessionPopularityResponse],
)
def get_session_popularity(
    event_id: int,
    current_user=Depends(
        require_roles("Event Organizer")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_session_popularity(
        event_id=event_id,
        organizer_id=current_user.id,
    )


# ============================================================
# LEVEL 15 REPORTS
# ============================================================

@router.get(
    "/reports/daily-registrations",
    response_model=list[DailyRegistrationReportResponse],
)
def get_daily_registration_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_daily_registrations(
        event_id=event_id
    )


@router.get(
    "/reports/event-revenue",
    response_model=list[EventRevenueReportResponse],
)
def get_event_revenue_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_event_revenue_report(
        event_id=event_id
    )


@router.get(
    "/reports/ticket-sales",
    response_model=list[TicketSalesReportResponse],
)
def get_ticket_sales_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_ticket_sales_report(
        event_id=event_id
    )


@router.get(
    "/reports/attendance",
    response_model=list[AttendanceReportResponse],
)
def get_attendance_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_attendance_report(
        event_id=event_id
    )


@router.get(
    "/reports/speaker-ratings",
    response_model=list[SpeakerRatingReportResponse],
)
def get_speaker_ratings_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_speaker_ratings_report(
        event_id=event_id
    )


@router.get(
    "/reports/session-popularity",
    response_model=list[SessionPopularityReportResponse],
)
def get_session_popularity_report(
    event_id: int | None = Query(
        default=None,
        ge=1,
    ),
    current_user=Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)

    return service.get_session_popularity_report(
        event_id=event_id
    )