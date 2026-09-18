from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.check_in import CheckInStatus


class CheckInCreate(BaseModel):
    attendee_id: int = Field(gt=0)
    event_id: int = Field(gt=0)


class CheckInUpdate(BaseModel):
    status: CheckInStatus


class CheckInResponse(BaseModel):
    id: int
    attendee_id: int
    event_id: int
    check_in_time: datetime
    check_out_time: datetime | None
    status: CheckInStatus

    model_config = ConfigDict(from_attributes=True)