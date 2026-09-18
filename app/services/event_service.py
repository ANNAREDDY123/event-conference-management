from fastapi import HTTPException, status

from app.models.event import Event, EventStatus
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole
from app.repositories.event_repository import EventRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.event import EventCreate, EventUpdate
from app.services.ticket_purchase_service import TicketPurchaseService


class EventService:

    def __init__(self, db):
        self.repository = EventRepository(db)
        self.notification_repository = NotificationRepository(db)
        self.ticket_purchase_service = TicketPurchaseService(db)

    # ============================================================
    # CREATE EVENT
    # ============================================================

    def create_event(
        self,
        event_data: EventCreate,
        current_user: User,
    ) -> Event:

        if current_user.role != UserRole.EVENT_ORGANIZER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Event Organizers can create events",
            )

        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizer account is inactive",
            )

        event = Event(
            event_name=event_data.event_name,
            description=event_data.description,
            event_type=event_data.event_type,
            organizer_id=current_user.id,
            start_date=event_data.start_date,
            end_date=event_data.end_date,
            registration_start=event_data.registration_start,
            registration_end=event_data.registration_end,
            capacity=event_data.capacity,
            status=event_data.status,
        )

        return self.repository.create(event)

    # ============================================================
    # GET EVENT
    # ============================================================

    def get_event(
        self,
        event_id: int,
    ) -> Event:

        event = self.repository.get_by_id(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return event

    # ============================================================
    # GET EVENTS
    # ============================================================

    def get_events(
        self,
        event_type=None,
        status=None,
        start_date=None,
        end_date=None,
        search=None,
        page=1,
        page_size=10,
        sort_by="start_date",
        sort_order="asc",
        available_capacity=None,
    ) -> list[Event]:

        return self.repository.get_all(
            event_type=event_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            available_capacity=available_capacity,
        )

    # ============================================================
    # UPDATE EVENT
    # ============================================================

    def update_event(
        self,
        event_id: int,
        event_data: EventUpdate,
        current_user: User,
    ) -> Event:

        event = self.get_event(event_id)

        # --------------------------------------------------------
        # Ownership / authorization
        # --------------------------------------------------------

        if (
            current_user.role != UserRole.ADMIN
            and event.organizer_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to update this event"
                ),
            )

        update_data = event_data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return event

        # --------------------------------------------------------
        # Validate combined dates
        # --------------------------------------------------------

        start_date = update_data.get(
            "start_date",
            event.start_date,
        )

        end_date = update_data.get(
            "end_date",
            event.end_date,
        )

        registration_start = update_data.get(
            "registration_start",
            event.registration_start,
        )

        registration_end = update_data.get(
            "registration_end",
            event.registration_end,
        )

        capacity = update_data.get(
            "capacity",
            event.capacity,
        )

        if end_date <= start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date must be after start date",
            )

        if registration_end > start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Registration closing date cannot "
                    "be after event start date"
                ),
            )

        if registration_end <= registration_start:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Registration end must be after "
                    "registration start"
                ),
            )

        if capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Capacity must be greater than zero",
            )

        # --------------------------------------------------------
        # Detect cancellation before updating
        # --------------------------------------------------------

        event_was_cancelled = (
            event.status != EventStatus.CANCELLED
            and update_data.get("status")
            == EventStatus.CANCELLED
        )

        # --------------------------------------------------------
        # Persist event update
        # --------------------------------------------------------

        updated_event = self.repository.update(
            event,
            update_data,
        )

        # --------------------------------------------------------
        # LEVEL 13 / LEVEL 16
        # EVENT CANCELLATION WORKFLOW
        # --------------------------------------------------------

        if event_was_cancelled:
            self._process_event_cancellation(
                event,
            )

        return updated_event

    # ============================================================
    # EVENT CANCELLATION
    # ============================================================

    def _process_event_cancellation(
        self,
        event: Event,
    ) -> None:

        # --------------------------------------------------------
        # 1. Notify attendees
        # --------------------------------------------------------

        attendees = (
            self.repository.get_attendees_by_event(
                event.id
            )
        )

        for attendee in attendees:

            notification = Notification(
                user_id=attendee.user_id,
                title="Event Cancelled",
                message=(
                    f"The event '{event.event_name}' "
                    "has been cancelled. "
                    "Please check the event details "
                    "for more information."
                ),
                notification_type=(
                    NotificationType.EVENT_CANCELLATION
                ),
            )

            self.notification_repository.create(
                notification
            )

        # --------------------------------------------------------
        # 2. Get successful confirmed purchases
        # --------------------------------------------------------

        successful_purchases = (
            self.repository
            .get_successful_purchases_by_event(
                event.id
            )
        )

        # --------------------------------------------------------
        # 3. Refund each successful purchase
        # --------------------------------------------------------

        for purchase in successful_purchases:

            self.ticket_purchase_service.refund_purchase(
                purchase.id
            )

    # ============================================================
    # DELETE EVENT
    # ============================================================

    def delete_event(
        self,
        event_id: int,
        current_user: User,
    ) -> None:

        event = self.get_event(event_id)

        # --------------------------------------------------------
        # Ownership / authorization
        # --------------------------------------------------------

        if (
            current_user.role != UserRole.ADMIN
            and event.organizer_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to delete this event"
                ),
            )

        self.repository.delete(event)