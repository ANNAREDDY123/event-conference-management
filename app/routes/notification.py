from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import NotificationStatus
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notification_service import NotificationService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a notification.

    Only an authenticated user can create a notification.
    """

    service = NotificationService(db)

    return service.create_notification(notification_data)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    status_filter: NotificationStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get notifications belonging to the current logged-in user.
    """

    service = NotificationService(db)

    return service.get_user_notifications(
        user_id=current_user.id,
        status=status_filter,
    )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as read.

    Ownership is validated using the current logged-in user.
    """

    service = NotificationService(db)

    return service.mark_notification_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a notification.

    Ownership is validated using the current logged-in user.
    """

    service = NotificationService(db)

    service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    return None