from fastapi import HTTPException, status

from app.models.certificate import Certificate
from app.models.event import EventStatus
from app.repositories.certificate_repository import CertificateRepository
from app.schemas.certificate import CertificateCreate


class CertificateService:
    def __init__(self, db):
        self.repository = CertificateRepository(db)

    def create_certificate(
        self,
        certificate_data: CertificateCreate,
    ) -> Certificate:
        # Validate attendee
        attendee = self.repository.get_attendee(
            certificate_data.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        # Validate event
        event = self.repository.get_event(
            certificate_data.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Ensure attendee belongs to the event
        if attendee.event_id != event.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendee is not registered for this event",
            )

        # Certificates should only be issued for completed events
        if event.status != EventStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certificate can only be issued for a completed event",
            )

        # Prevent duplicate certificate
        existing_certificate = self.repository.get_existing_certificate(
            attendee_id=certificate_data.attendee_id,
            event_id=certificate_data.event_id,
        )

        if existing_certificate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Certificate already exists for this attendee and event",
            )

        # Generate certificate number
        certificate_number = self._generate_certificate_number(
            event.id
        )

        certificate = Certificate(
            attendee_id=certificate_data.attendee_id,
            event_id=certificate_data.event_id,
            certificate_number=certificate_number,
            certificate_type=certificate_data.certificate_type,
        )

        return self.repository.create(certificate)

    def _generate_certificate_number(
        self,
        event_id: int,
    ) -> str:
        # Generate a unique certificate number.
        # Example: CERT-E1-000001
        existing_count = len(self.repository.get_all()) + 1

        certificate_number = (
            f"CERT-E{event_id}-{existing_count:06d}"
        )

        # Make sure the generated number is unique
        while self.repository.get_by_certificate_number(
            certificate_number
        ):
            existing_count += 1
            certificate_number = (
                f"CERT-E{event_id}-{existing_count:06d}"
            )

        return certificate_number

    def get_certificate(
        self,
        certificate_id: int,
    ) -> Certificate:
        certificate = self.repository.get_by_id(
            certificate_id
        )

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found",
            )

        return certificate

    def get_certificates(self) -> list[Certificate]:
        return self.repository.get_all()

    def get_certificates_by_attendee(
        self,
        attendee_id: int,
    ) -> list[Certificate]:
        attendee = self.repository.get_attendee(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return self.repository.get_by_attendee(
            attendee_id
        )

    def get_certificates_by_event(
        self,
        event_id: int,
    ) -> list[Certificate]:
        event = self.repository.get_event(
            event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return self.repository.get_by_event(
            event_id
        )

    def delete_certificate(
        self,
        certificate_id: int,
    ) -> None:
        certificate = self.repository.get_by_id(
            certificate_id
        )

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found",
            )

        self.repository.delete(certificate)