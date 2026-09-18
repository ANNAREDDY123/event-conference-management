from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketType(str, Enum):
    REGULAR = "Regular"
    VIP = "VIP"
    EARLY_BIRD = "Early Bird"


class TicketStatus(str, Enum):
    AVAILABLE = "Available"
    SOLD_OUT = "Sold Out"
    INACTIVE = "Inactive"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    ticket_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    ticket_type: Mapped[TicketType] = mapped_column(
        SQLEnum(TicketType),
        nullable=False,
        index=True,
    )

    price: Mapped[float] = mapped_column(
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus),
        default=TicketStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    event = relationship("Event", backref="tickets")