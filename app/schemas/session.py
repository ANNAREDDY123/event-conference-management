from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.session import SessionStatus, SessionType


class SessionCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    speaker_id: int | None = Field(default=None, gt=0)
    hall_id: int = Field(..., gt=0)

    title: str = Field(..., min_length=2, max_length=200)
    description: str | None = None

    session_type: SessionType

    start_time: datetime
    end_time: datetime

    capacity: int = Field(..., gt=0)

    status: SessionStatus = SessionStatus.SCHEDULED


class SessionUpdate(BaseModel):
    speaker_id: int | None = Field(default=None, gt=0)
    hall_id: int | None = Field(default=None, gt=0)

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    session_type: SessionType | None = None

    start_time: datetime | None = None
    end_time: datetime | None = None

    capacity: int | None = Field(default=None, gt=0)

    status: SessionStatus | None = None


class SessionResponse(BaseModel):
    id: int
    event_id: int
    speaker_id: int | None
    hall_id: int

    title: str
    description: str | None

    session_type: SessionType

    start_time: datetime
    end_time: datetime

    capacity: int

    status: SessionStatus

    model_config = ConfigDict(from_attributes=True)