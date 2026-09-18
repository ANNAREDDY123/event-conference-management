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


class BookingStatus(str, Enum):
    BOOKED = "Booked"
    CANCELLED = "Cancelled"


class SessionBooking(Base):
    __tablename__ = "session_bookings"

    __table_args__ = (
        UniqueConstraint(
            "attendee_id",
            "session_id",
            name="uq_attendee_session_booking",
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

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"),
        nullable=False,
        index=True,
    )

    booking_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus),
        default=BookingStatus.BOOKED,
        nullable=False,
        index=True,
    )

    attendee = relationship(
        "Attendee",
        backref="session_bookings",
    )

    session = relationship(
        "EventSession",
        backref="bookings",
    )