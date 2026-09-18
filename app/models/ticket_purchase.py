from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class PurchaseStatus(str, Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class TicketPurchase(Base):
    __tablename__ = "ticket_purchases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"),
        nullable=False,
        index=True,
    )

    attendee_id: Mapped[int] = mapped_column(
        ForeignKey("attendees.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )

    purchase_status: Mapped[PurchaseStatus] = mapped_column(
        SQLEnum(PurchaseStatus),
        default=PurchaseStatus.CONFIRMED,
        nullable=False,
        index=True,
    )

    payment_reference: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    purchase_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    ticket = relationship("Ticket", backref="purchases")
    attendee = relationship("Attendee", backref="ticket_purchases")