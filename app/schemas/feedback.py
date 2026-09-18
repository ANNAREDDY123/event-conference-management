from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    attendee_id: int = Field(gt=0)
    event_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    comments: str | None = Field(
        default=None,
        max_length=1000,
    )


class FeedbackUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    comments: str | None = Field(
        default=None,
        max_length=1000,
    )


class FeedbackResponse(BaseModel):
    id: int
    attendee_id: int
    event_id: int
    rating: int
    comments: str | None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)