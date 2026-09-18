from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketStatus, TicketType


class TicketCreate(BaseModel):
    event_id: int = Field(gt=0)
    ticket_name: str = Field(min_length=2, max_length=150)
    ticket_type: TicketType
    price: float = Field(ge=0)
    quantity: int = Field(gt=0)
    status: TicketStatus = TicketStatus.AVAILABLE


class TicketUpdate(BaseModel):
    ticket_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    ticket_type: TicketType | None = None
    price: float | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, gt=0)
    status: TicketStatus | None = None


class TicketResponse(BaseModel):
    id: int
    event_id: int
    ticket_name: str
    ticket_type: TicketType
    price: float
    quantity: int
    available_quantity: int
    status: TicketStatus

    model_config = ConfigDict(from_attributes=True)