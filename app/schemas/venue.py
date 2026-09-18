from pydantic import BaseModel, ConfigDict, Field

from app.models.venue import (
    HallAvailabilityStatus,
    VenueStatus,
)


# =========================================================
# Venue Schemas
# =========================================================

class VenueCreate(BaseModel):
    venue_name: str = Field(
        min_length=2,
        max_length=200,
    )
    address: str = Field(
        min_length=2,
    )
    city: str = Field(
        min_length=2,
        max_length=100,
    )
    capacity: int = Field(
        gt=0,
    )
    facilities: str | None = None
    status: VenueStatus = VenueStatus.ACTIVE


class VenueUpdate(BaseModel):
    venue_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )
    address: str | None = Field(
        default=None,
        min_length=2,
    )
    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    capacity: int | None = Field(
        default=None,
        gt=0,
    )
    facilities: str | None = None
    status: VenueStatus | None = None


class VenueResponse(BaseModel):
    id: int
    venue_name: str
    address: str
    city: str
    capacity: int
    facilities: str | None
    status: VenueStatus

    model_config = ConfigDict(
        from_attributes=True,
    )


# =========================================================
# Hall Schemas
# =========================================================

class HallCreate(BaseModel):
    hall_name: str = Field(
        min_length=2,
        max_length=200,
    )
    capacity: int = Field(
        gt=0,
    )
    floor: int
    availability_status: HallAvailabilityStatus = (
        HallAvailabilityStatus.AVAILABLE
    )


class HallUpdate(BaseModel):
    hall_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )
    capacity: int | None = Field(
        default=None,
        gt=0,
    )
    floor: int | None = None
    availability_status: HallAvailabilityStatus | None = None


class HallResponse(BaseModel):
    id: int
    venue_id: int
    hall_name: str
    capacity: int
    floor: int
    availability_status: HallAvailabilityStatus

    model_config = ConfigDict(
        from_attributes=True,
    )