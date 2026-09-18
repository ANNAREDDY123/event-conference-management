from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.ticket_purchase import TicketPurchase
from app.models.user import User


class TicketPurchaseRepository:

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # PURCHASE OPERATIONS
    # ============================================================

    def create(
        self,
        purchase: TicketPurchase,
    ) -> TicketPurchase:

        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)

        return purchase

    def get_by_id(
        self,
        purchase_id: int,
    ) -> TicketPurchase | None:

        statement = select(TicketPurchase).where(
            TicketPurchase.id == purchase_id
        )

        return self.db.scalar(statement)

    def get_by_attendee(
        self,
        attendee_id: int,
    ) -> list[TicketPurchase]:

        statement = (
            select(TicketPurchase)
            .where(
                TicketPurchase.attendee_id == attendee_id
            )
            .order_by(
                TicketPurchase.purchase_date
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_ticket(
        self,
        ticket_id: int,
    ) -> list[TicketPurchase]:

        statement = (
            select(TicketPurchase)
            .where(
                TicketPurchase.ticket_id == ticket_id
            )
            .order_by(
                TicketPurchase.purchase_date
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_all(self) -> list[TicketPurchase]:

        statement = (
            select(TicketPurchase)
            .order_by(
                TicketPurchase.purchase_date
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ============================================================
    # RELATED ENTITY OPERATIONS
    # ============================================================

    def get_attendee(
        self,
        attendee_id: int,
    ) -> Attendee | None:

        statement = select(Attendee).where(
            Attendee.id == attendee_id
        )

        return self.db.scalar(statement)

    def get_event(
        self,
        event_id: int,
    ) -> Event | None:

        statement = select(Event).where(
            Event.id == event_id
        )

        return self.db.scalar(statement)

    def get_event_by_attendee(
        self,
        attendee_id: int,
    ) -> Event | None:

        statement = (
            select(Event)
            .join(
                Attendee,
                Attendee.event_id == Event.id,
            )
            .where(
                Attendee.id == attendee_id
            )
        )

        return self.db.scalar(statement)

    def get_user(
        self,
        user_id: int,
    ) -> User | None:

        statement = select(User).where(
            User.id == user_id
        )

        return self.db.scalar(statement)

    def get_ticket(
        self,
        ticket_id: int,
    ) -> Ticket | None:

        statement = select(Ticket).where(
            Ticket.id == ticket_id
        )

        return self.db.scalar(statement)

    # ============================================================
    # NOTIFICATION OPERATIONS
    # ============================================================

    def create_notification(
        self,
        notification: Notification,
    ) -> Notification:

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        purchase: TicketPurchase,
    ) -> TicketPurchase:

        self.db.commit()
        self.db.refresh(purchase)

        return purchase