from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.certificate import (
    CertificateCreate,
    CertificateResponse,
)
from app.services.certificate_service import CertificateService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"],
)


@router.post(
    "",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_certificate(
    certificate_data: CertificateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CertificateService(db).create_certificate(
        certificate_data
    )


@router.get(
    "",
    response_model=list[CertificateResponse],
)
def get_certificates(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CertificateService(db).get_certificates()


@router.get(
    "/attendee/{attendee_id}",
    response_model=list[CertificateResponse],
)
def get_certificates_by_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CertificateService(db).get_certificates_by_attendee(
        attendee_id
    )


@router.get(
    "/event/{event_id}",
    response_model=list[CertificateResponse],
)
def get_certificates_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CertificateService(db).get_certificates_by_event(
        event_id
    )


@router.get(
    "/{certificate_id}",
    response_model=CertificateResponse,
)
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return CertificateService(db).get_certificate(
        certificate_id
    )


@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    CertificateService(db).delete_certificate(
        certificate_id
    )