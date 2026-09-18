from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.event import EventStatus, EventType


class EventCreate(BaseModel):
    event_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    event_type: EventType

    start_date: datetime

    end_date: datetime

    registration_start: datetime

    registration_end: datetime

    capacity: int = Field(
        ...,
        gt=0,
    )

    status: EventStatus = EventStatus.DRAFT

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError(
                "End date must be after start date"
            )

        if self.registration_end > self.start_date:
            raise ValueError(
                "Registration closing date cannot be after event start date"
            )

        if self.registration_end <= self.registration_start:
            raise ValueError(
                "Registration end must be after registration start"
            )

        return self


class EventUpdate(BaseModel):
    event_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    event_type: EventType | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None

    registration_start: datetime | None = None

    registration_end: datetime | None = None

    capacity: int | None = Field(
        default=None,
        gt=0,
    )

    status: EventStatus | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        provided = self.model_fields_set

        start_date = self.start_date
        end_date = self.end_date
        registration_start = self.registration_start
        registration_end = self.registration_end

        if (
            "start_date" in provided
            and "end_date" in provided
            and start_date is not None
            and end_date is not None
            and end_date <= start_date
        ):
            raise ValueError(
                "End date must be after start date"
            )

        if (
            "registration_end" in provided
            and "start_date" in provided
            and registration_end is not None
            and start_date is not None
            and registration_end > start_date
        ):
            raise ValueError(
                "Registration closing date cannot be after event start date"
            )

        if (
            "registration_start" in provided
            and "registration_end" in provided
            and registration_start is not None
            and registration_end is not None
            and registration_end <= registration_start
        ):
            raise ValueError(
                "Registration end must be after registration start"
            )

        return self


class EventResponse(BaseModel):
    id: int
    event_name: str
    description: str | None
    event_type: EventType
    organizer_id: int
    start_date: datetime
    end_date: datetime
    registration_start: datetime
    registration_end: datetime
    capacity: int
    status: EventStatus

    model_config = ConfigDict(
        from_attributes=True,
    )