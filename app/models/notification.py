from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationType(str, Enum):
    REGISTRATION = "Registration"
    TICKET_PURCHASE = "Ticket Purchase"
    PAYMENT = "Payment"
    SESSION_BOOKING = "Session Booking"
    EVENT_CANCELLATION = "Event Cancellation"
    REFUND = "Refund"
    CERTIFICATE = "Certificate"
    GENERAL = "General"


class NotificationStatus(str, Enum):
    UNREAD = "Unread"
    READ = "Read"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.UNREAD,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    user = relationship(
        "User",
        backref="notifications",
    )