from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.check_in import (
    CheckInCreate,
    CheckInResponse,
    CheckInUpdate,
)
from app.services.check_in_service import CheckInService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/check-ins",
    tags=["Check-Ins"],
)


@router.post(
    "",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_check_in(
    check_in_data: CheckInCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).create_check_in(check_in_data)


@router.get(
    "",
    response_model=list[CheckInResponse],
)
def get_check_ins(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).get_check_ins()


@router.get(
    "/attendee/{attendee_id}",
    response_model=list[CheckInResponse],
)
def get_check_ins_by_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).get_check_ins_by_attendee(attendee_id)


@router.get(
    "/event/{event_id}",
    response_model=list[CheckInResponse],
)
def get_check_ins_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).get_check_ins_by_event(event_id)


@router.get(
    "/{check_in_id}",
    response_model=CheckInResponse,
)
def get_check_in(
    check_in_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).get_check_in(check_in_id)


@router.put(
    "/{check_in_id}",
    response_model=CheckInResponse,
)
def update_check_in(
    check_in_id: int,
    check_in_data: CheckInUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).update_check_in(
        check_in_id,
        check_in_data,
    )


@router.put(
    "/{check_in_id}/checkout",
    response_model=CheckInResponse,
)
def check_out(
    check_in_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CheckInService(db).check_out(check_in_id)


@router.delete(
    "/{check_in_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_check_in(
    check_in_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    CheckInService(db).delete_check_in(check_in_id)