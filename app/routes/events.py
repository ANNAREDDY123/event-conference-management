from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import EventStatus, EventType
from app.models.user import User, UserRole
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event_service import EventService
from app.utils.dependencies import (
    get_current_active_user,
    require_roles,
)


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.EVENT_ORGANIZER)
    ),
):
    service = EventService(db)

    return service.create_event(
        event_data,
        current_user,
    )


@router.get(
    "",
    response_model=list[EventResponse],
)
def get_events(
    event_type: EventType | None = Query(
        default=None,
    ),
    event_status: EventStatus | None = Query(
        default=None,
        alias="status",
    ),
    start_date: datetime | None = Query(
        default=None,
    ),
    end_date: datetime | None = Query(
        default=None,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="start_date",
        pattern="^(event_name|start_date|end_date|capacity|status|event_type)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    available_capacity: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = EventService(db)

    return service.get_events(
        event_type=event_type,
        status=event_status,
        start_date=start_date,
        end_date=end_date,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        available_capacity=available_capacity,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = EventService(db)

    return service.get_event(event_id)


@router.put(
    "/{event_id}",
    response_model=EventResponse,
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = EventService(db)

    return service.update_event(
        event_id,
        event_data,
        current_user,
    )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = EventService(db)

    service.delete_event(
        event_id,
        current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )