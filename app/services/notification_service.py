from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate


class NotificationService:
    """
    Service layer for Notification business logic.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    def create_notification(
        self,
        notification_data: NotificationCreate,
    ) -> Notification:
        """
        Create a new notification.
        """

        notification = Notification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
        )

        return self.repository.create(notification)

    def get_user_notifications(
        self,
        user_id: int,
        status=None,
    ) -> list[Notification]:
        """
        Get all notifications belonging to a specific user.
        """

        return self.repository.get_by_user(
            user_id=user_id,
            status=status,
        )

    def mark_notification_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        """
        Mark a notification as read after verifying ownership.
        """

        notification = self.repository.get_by_id(notification_id)

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this notification",
            )

        return self.repository.mark_as_read(notification)

    def delete_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> None:
        """
        Delete a notification after verifying ownership.
        """

        notification = self.repository.get_by_id(notification_id)

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this notification",
            )

        self.repository.delete(notification)