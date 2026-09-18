from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)
from app.services.ticket_service import TicketService
from app.utils.dependencies import get_current_active_user


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    return service.create_ticket(ticket_data)


@router.get(
    "",
    response_model=list[TicketResponse],
)
def get_tickets(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    return service.get_tickets()


@router.get(
    "/event/{event_id}",
    response_model=list[TicketResponse],
)
def get_tickets_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    return service.get_tickets_by_event(event_id)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    return service.get_ticket(ticket_id)


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    return service.update_ticket(ticket_id, ticket_data)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TicketService(db)
    service.delete_ticket(ticket_id)