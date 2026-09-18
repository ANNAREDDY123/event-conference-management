from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CheckInStatus(str, Enum):
    CHECKED_IN = "Checked In"
    CHECKED_OUT = "Checked Out"


class CheckIn(Base):
    __tablename__ = "check_ins"

    __table_args__ = (
        UniqueConstraint(
            "attendee_id",
            "event_id",
            name="uq_attendee_event_checkin",
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

    check_in_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    check_out_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[CheckInStatus] = mapped_column(
        SQLEnum(CheckInStatus),
        default=CheckInStatus.CHECKED_IN,
        nullable=False,
        index=True,
    )

    attendee = relationship(
        "Attendee",
        backref="check_ins",
    )

    event = relationship(
        "Event",
        backref="check_ins",
    )