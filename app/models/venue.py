from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VenueStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class HallAvailabilityStatus(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    venue_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    facilities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[VenueStatus] = mapped_column(
        SQLEnum(VenueStatus),
        default=VenueStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    halls = relationship(
        "Hall",
        back_populates="venue",
        cascade="all, delete-orphan",
    )


class Hall(Base):
    __tablename__ = "halls"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.id"),
        nullable=False,
        index=True,
    )

    hall_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    floor: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    availability_status: Mapped[HallAvailabilityStatus] = mapped_column(
        SQLEnum(HallAvailabilityStatus),
        default=HallAvailabilityStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    venue = relationship(
        "Venue",
        back_populates="halls",
    )