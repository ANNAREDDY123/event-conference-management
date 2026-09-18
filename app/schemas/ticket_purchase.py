from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket_purchase import PaymentStatus, PurchaseStatus


class TicketPurchaseCreate(BaseModel):
    ticket_id: int = Field(gt=0)
    attendee_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class TicketPurchaseResponse(BaseModel):
    id: int
    ticket_id: int
    attendee_id: int
    quantity: int
    total_amount: float
    payment_status: PaymentStatus
    purchase_status: PurchaseStatus
    payment_reference: str | None
    purchase_date: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus