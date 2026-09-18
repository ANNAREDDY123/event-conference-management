from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.attendee import (
    AttendeeCreate,
    AttendeeResponse,
    AttendeeStatusUpdate,
)
from app.services.attendee_service import AttendeeService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/attendees",
    tags=["Attendees"],
)


@router.post(
    "",
    response_model=AttendeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_attendee(
    attendee_data: AttendeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.register_attendee(
        attendee_data
    )


@router.get(
    "",
    response_model=list[AttendeeResponse],
)
def get_attendees(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.get_attendees()


@router.get(
    "/{attendee_id}",
    response_model=AttendeeResponse,
)
def get_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.get_attendee(
        attendee_id
    )


@router.get(
    "/event/{event_id}",
    response_model=list[AttendeeResponse],
)
def get_attendees_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.get_attendees_by_event(
        event_id
    )


# ============================================================
# LEVEL 16 - CANCELLATION
# ============================================================

@router.put(
    "/{attendee_id}/cancel",
    response_model=AttendeeResponse,
)
def cancel_attendee_registration(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.cancel_registration(
        attendee_id
    )


@router.put(
    "/{attendee_id}/status",
    response_model=AttendeeResponse,
)
def update_attendee_status(
    attendee_id: int,
    attendee_data: AttendeeStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = AttendeeService(db)

    return service.update_registration_status(
        attendee_id,
        attendee_data,
    )