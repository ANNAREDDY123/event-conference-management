from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CertificateCreate(BaseModel):
    attendee_id: int = Field(gt=0)
    event_id: int = Field(gt=0)
    certificate_type: str = Field(
        default="Participation",
        min_length=2,
        max_length=50,
    )


class CertificateResponse(BaseModel):
    id: int
    attendee_id: int
    event_id: int
    certificate_number: str
    issue_date: datetime
    certificate_type: str

    model_config = ConfigDict(from_attributes=True)