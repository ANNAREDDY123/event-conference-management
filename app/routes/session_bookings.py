from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.session_booking import (
    SessionBookingCreate,
    SessionBookingResponse,
    SessionBookingUpdate,
)
from app.services.session_booking_service import SessionBookingService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/session-bookings",
    tags=["Session Bookings"],
)


@router.post(
    "",
    response_model=SessionBookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session_booking(
    booking_data: SessionBookingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).create_booking(booking_data)


@router.get(
    "",
    response_model=list[SessionBookingResponse],
)
def get_session_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).get_bookings()


@router.get(
    "/attendee/{attendee_id}",
    response_model=list[SessionBookingResponse],
)
def get_bookings_by_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).get_bookings_by_attendee(attendee_id)


@router.get(
    "/session/{session_id}",
    response_model=list[SessionBookingResponse],
)
def get_bookings_by_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).get_bookings_by_session(session_id)


@router.get(
    "/{booking_id}",
    response_model=SessionBookingResponse,
)
def get_session_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).get_booking(booking_id)


@router.put(
    "/{booking_id}",
    response_model=SessionBookingResponse,
)
def update_session_booking(
    booking_id: int,
    booking_data: SessionBookingUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).update_booking(
        booking_id,
        booking_data,
    )


@router.put(
    "/{booking_id}/cancel",
    response_model=SessionBookingResponse,
)
def cancel_session_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return SessionBookingService(db).cancel_booking(booking_id)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    SessionBookingService(db).delete_booking(booking_id)