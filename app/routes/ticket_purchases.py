from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ticket_purchase import (
    PaymentUpdate,
    TicketPurchaseCreate,
    TicketPurchaseResponse,
)
from app.services.ticket_purchase_service import TicketPurchaseService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/ticket-purchases",
    tags=["Ticket Purchases"],
)


@router.post(
    "",
    response_model=TicketPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_purchase(
    purchase_data: TicketPurchaseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.create_purchase(purchase_data)


@router.get(
    "",
    response_model=list[TicketPurchaseResponse],
)
def get_ticket_purchases(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.get_all_purchases()


@router.get(
    "/attendee/{attendee_id}",
    response_model=list[TicketPurchaseResponse],
)
def get_purchases_by_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.get_purchases_by_attendee(attendee_id)


@router.get(
    "/ticket/{ticket_id}",
    response_model=list[TicketPurchaseResponse],
)
def get_purchases_by_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.get_purchases_by_ticket(ticket_id)


@router.get(
    "/{purchase_id}",
    response_model=TicketPurchaseResponse,
)
def get_ticket_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.get_purchase(purchase_id)


@router.put(
    "/{purchase_id}/payment",
    response_model=TicketPurchaseResponse,
)
def update_payment(
    purchase_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.update_payment(
        purchase_id,
        payment_data,
    )


@router.put(
    "/{purchase_id}/refund",
    response_model=TicketPurchaseResponse,
)
def refund_ticket_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TicketPurchaseService(db)

    return service.refund_purchase(purchase_id)