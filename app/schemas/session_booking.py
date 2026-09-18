from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.session_booking import BookingStatus


class SessionBookingCreate(BaseModel):
    attendee_id: int = Field(gt=0)
    session_id: int = Field(gt=0)


class SessionBookingUpdate(BaseModel):
    status: BookingStatus


class SessionBookingResponse(BaseModel):
    id: int
    attendee_id: int
    session_id: int
    booking_date: datetime
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)