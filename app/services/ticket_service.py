from fastapi import HTTPException, status

from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:

    def __init__(self, db):
        self.repository = TicketRepository(db)

    # ============================================================
    # CREATE TICKET
    # ============================================================

    def create_ticket(
        self,
        ticket_data: TicketCreate,
    ) -> Ticket:

        # Check event exists
        event = self.repository.get_event(
            ticket_data.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Ticket quantity cannot exceed event capacity
        existing_tickets = self.repository.get_by_event(
            ticket_data.event_id
        )

        total_quantity = sum(
            ticket.quantity
            for ticket in existing_tickets
        )

        if total_quantity + ticket_data.quantity > event.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total ticket quantity cannot exceed event capacity",
            )

        ticket = Ticket(
            event_id=ticket_data.event_id,
            ticket_name=ticket_data.ticket_name,
            ticket_type=ticket_data.ticket_type,
            price=ticket_data.price,
            quantity=ticket_data.quantity,
            available_quantity=ticket_data.quantity,
            status=ticket_data.status,
        )

        return self.repository.create(ticket)

    # ============================================================
    # GET TICKET
    # ============================================================

    def get_ticket(
        self,
        ticket_id: int,
    ) -> Ticket:

        ticket = self.repository.get_by_id(
            ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return ticket

    # ============================================================
    # GET ALL TICKETS
    # ============================================================

    def get_tickets(
        self,
    ) -> list[Ticket]:

        return self.repository.get_all()

    # ============================================================
    # GET TICKETS BY EVENT
    # ============================================================

    def get_tickets_by_event(
        self,
        event_id: int,
    ) -> list[Ticket]:

        event = self.repository.get_event(
            event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return self.repository.get_by_event(
            event_id
        )

    # ============================================================
    # UPDATE TICKET
    # ============================================================

    def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
    ) -> Ticket:

        ticket = self.get_ticket(ticket_id)

        update_data = ticket_data.model_dump(
            exclude_unset=True
        )

        if "quantity" in update_data:

            new_quantity = update_data["quantity"]

            sold_quantity = (
                ticket.quantity
                - ticket.available_quantity
            )

            if new_quantity < sold_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ticket quantity cannot be less than already sold quantity",
                )

            update_data["available_quantity"] = (
                new_quantity - sold_quantity
            )

        for field, value in update_data.items():
            setattr(ticket, field, value)

        return self.repository.update(ticket)

    # ============================================================
    # DELETE TICKET
    # ============================================================

    def delete_ticket(
        self,
        ticket_id: int,
    ) -> None:

        ticket = self.get_ticket(ticket_id)

        self.repository.delete(ticket)