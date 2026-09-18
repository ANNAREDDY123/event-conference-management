from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event, EventStatus, EventType
from app.models.session import EventSession
from app.models.ticket import Ticket
from app.models.ticket_purchase import (
    PaymentStatus,
    PurchaseStatus,
    TicketPurchase,
)
from app.models.venue import Hall, Venue


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # CREATE
    # ============================================================

    def create(self, event: Event) -> Event:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    # ============================================================
    # GET
    # ============================================================

    def get_by_id(self, event_id: int) -> Event | None:
        statement = select(Event).where(Event.id == event_id)
        return self.db.scalar(statement)

    def get_all(
        self,
        event_type: EventType | None = None,
        status: EventStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "start_date",
        sort_order: str = "asc",
        available_capacity: bool | None = None,
    ) -> list[Event]:

        statement = select(Event)

        # ---------------------------------------------------------
        # Filters
        # ---------------------------------------------------------

        if event_type is not None:
            statement = statement.where(
                Event.event_type == event_type
            )

        if status is not None:
            statement = statement.where(
                Event.status == status
            )

        if start_date is not None:
            statement = statement.where(
                Event.start_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                Event.end_date <= end_date
            )

        # ---------------------------------------------------------
        # Search
        # ---------------------------------------------------------

        if search:
            search_pattern = f"%{search.strip()}%"

            statement = statement.where(
                or_(
                    Event.event_name.ilike(search_pattern),
                    Event.description.ilike(search_pattern),
                )
            )

        # ---------------------------------------------------------
        # Available capacity
        # ---------------------------------------------------------

        if available_capacity is True:
            attendee_count_subquery = (
                select(func.count())
                .select_from(Attendee)
                .where(Attendee.event_id == Event.id)
                .correlate(Event)
                .scalar_subquery()
            )

            statement = statement.where(
                attendee_count_subquery < Event.capacity
            )

        # ---------------------------------------------------------
        # Sorting
        # ---------------------------------------------------------

        sort_columns = {
            "event_name": Event.event_name,
            "start_date": Event.start_date,
            "end_date": Event.end_date,
            "capacity": Event.capacity,
            "status": Event.status,
            "event_type": Event.event_type,
        }

        sort_column = sort_columns.get(
            sort_by,
            Event.start_date,
        )

        if sort_order.lower() == "desc":
            statement = statement.order_by(
                sort_column.desc()
            )
        else:
            statement = statement.order_by(
                sort_column.asc()
            )

        # ---------------------------------------------------------
        # Pagination
        # ---------------------------------------------------------

        offset = (page - 1) * page_size

        statement = (
            statement
            .offset(offset)
            .limit(page_size)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        event: Event,
        update_data: dict,
    ) -> Event:

        for field, value in update_data.items():
            setattr(event, field, value)

        self.db.commit()
        self.db.refresh(event)

        return event

    # ============================================================
    # DELETE
    # ============================================================

    def delete(self, event: Event) -> None:
        self.db.delete(event)
        self.db.commit()

    # ============================================================
    # LEVEL 18 - EVENT CANCELLATION DATA ACCESS
    # ============================================================

    def get_attendees_by_event(
        self,
        event_id: int,
    ) -> list[Attendee]:

        statement = (
            select(Attendee)
            .where(Attendee.event_id == event_id)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_successful_purchases_by_event(
        self,
        event_id: int,
    ) -> list[TicketPurchase]:

        statement = (
            select(TicketPurchase)
            .join(
                Ticket,
                Ticket.id == TicketPurchase.ticket_id,
            )
            .where(
                Ticket.event_id == event_id,
                TicketPurchase.payment_status
                == PaymentStatus.SUCCESS,
                TicketPurchase.purchase_status
                == PurchaseStatus.CONFIRMED,
            )
        )

        return list(
            self.db.scalars(statement).all()
        )