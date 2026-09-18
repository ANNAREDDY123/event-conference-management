from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventType(str, Enum):
    CONFERENCE = "Conference"
    WORKSHOP = "Workshop"
    SEMINAR = "Seminar"
    MEETUP = "Meetup"
    TRAINING = "Training"


class EventStatus(str, Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    REGISTRATION_OPEN = "Registration Open"
    REGISTRATION_CLOSED = "Registration Closed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    event_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(EventType),
        nullable=False,
        index=True,
    )

    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    registration_start: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    registration_end: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus),
        default=EventStatus.DRAFT,
        nullable=False,
        index=True,
    )

    organizer = relationship(
        "User",
        backref="events",
    )