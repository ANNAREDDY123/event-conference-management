from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SessionType(str, Enum):
    KEYNOTE = "Keynote"
    WORKSHOP = "Workshop"
    PANEL = "Panel"
    TECHNICAL = "Technical"
    NETWORKING = "Networking"
    GENERAL = "General"


class SessionStatus(str, Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class EventSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    speaker_id: Mapped[int | None] = mapped_column(
        ForeignKey("speakers.id"),
        nullable=True,
        index=True,
    )

    hall_id: Mapped[int] = mapped_column(
        ForeignKey("halls.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    session_type: Mapped[SessionType] = mapped_column(
        SQLEnum(SessionType),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus),
        default=SessionStatus.SCHEDULED,
        nullable=False,
        index=True,
    )

    event = relationship("Event", backref="sessions")
    speaker = relationship("Speaker", backref="sessions")
    hall = relationship("Hall", backref="sessions")