from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    __table_args__ = (
        UniqueConstraint(
            "attendee_id",
            "event_id",
            name="uq_attendee_event_certificate",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    attendee_id: Mapped[int] = mapped_column(
        ForeignKey("attendees.id"),
        nullable=False,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    certificate_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    issue_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    certificate_type: Mapped[str] = mapped_column(
        String(50),
        default="Participation",
        nullable=False,
    )

    attendee = relationship(
        "Attendee",
        backref="certificates",
    )

    event = relationship(
        "Event",
        backref="certificates",
    )