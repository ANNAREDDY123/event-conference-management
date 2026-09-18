from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.certificate import Certificate
from app.models.event import Event


class CertificateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_attendee(self, attendee_id: int) -> Attendee | None:
        return self.db.get(Attendee, attendee_id)

    def get_event(self, event_id: int) -> Event | None:
        return self.db.get(Event, event_id)

    def create(self, certificate: Certificate) -> Certificate:
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        return certificate

    def get_by_id(self, certificate_id: int) -> Certificate | None:
        return self.db.get(Certificate, certificate_id)

    def get_by_attendee(self, attendee_id: int) -> list[Certificate]:
        statement = (
            select(Certificate)
            .where(Certificate.attendee_id == attendee_id)
            .order_by(Certificate.id)
        )
        return list(self.db.scalars(statement).all())

    def get_by_event(self, event_id: int) -> list[Certificate]:
        statement = (
            select(Certificate)
            .where(Certificate.event_id == event_id)
            .order_by(Certificate.id)
        )
        return list(self.db.scalars(statement).all())

    def get_existing_certificate(
        self,
        attendee_id: int,
        event_id: int,
    ) -> Certificate | None:
        statement = select(Certificate).where(
            Certificate.attendee_id == attendee_id,
            Certificate.event_id == event_id,
        )
        return self.db.scalars(statement).first()

    def get_by_certificate_number(
        self,
        certificate_number: str,
    ) -> Certificate | None:
        statement = select(Certificate).where(
            Certificate.certificate_number == certificate_number
        )
        return self.db.scalars(statement).first()

    def get_all(self) -> list[Certificate]:
        statement = select(Certificate).order_by(Certificate.id)
        return list(self.db.scalars(statement).all())

    def delete(self, certificate: Certificate) -> None:
        self.db.delete(certificate)
        self.db.commit()