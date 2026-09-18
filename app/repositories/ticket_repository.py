from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.ticket import Ticket


class TicketRepository:

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # TICKET OPERATIONS
    # ============================================================

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_by_id(
        self,
        ticket_id: int,
    ) -> Ticket | None:

        statement = select(Ticket).where(
            Ticket.id == ticket_id
        )

        return self.db.scalar(statement)

    def get_by_event(
        self,
        event_id: int,
    ) -> list[Ticket]:

        statement = (
            select(Ticket)
            .where(Ticket.event_id == event_id)
            .order_by(Ticket.id)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_all(self) -> list[Ticket]:

        statement = select(Ticket).order_by(
            Ticket.id
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ============================================================
    # RELATED EVENT OPERATIONS
    # ============================================================

    def get_event(
        self,
        event_id: int,
    ) -> Event | None:

        statement = select(Event).where(
            Event.id == event_id
        )

        return self.db.scalar(statement)

    # ============================================================
    # UPDATE / DELETE
    # ============================================================

    def update(
        self,
        ticket: Ticket,
    ) -> Ticket:

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def delete(
        self,
        ticket: Ticket,
    ) -> None:

        self.db.delete(ticket)
        self.db.commit()