from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttendeeCreate(BaseModel):
    user_id: int = Field(gt=0)
    event_id: int = Field(gt=0)


class AttendeeStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=30)


class AttendeeResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)