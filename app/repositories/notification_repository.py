from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationStatus,
)


class NotificationRepository:
    """
    Repository layer for Notification database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        """
        Create and save a new notification.
        """
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: int) -> Notification | None:
        """
        Get a notification by its ID.
        """
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    def get_by_user(
        self,
        user_id: int,
        status: NotificationStatus | None = None,
    ) -> list[Notification]:
        """
        Get all notifications belonging to a user.

        Optionally filter notifications by status.
        """
        query = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
        )

        if status is not None:
            query = query.filter(Notification.status == status)

        return (
            query
            .order_by(Notification.created_at.desc())
            .all()
        )

    def mark_as_read(
        self,
        notification: Notification,
    ) -> Notification:
        """
        Mark a notification as read.
        """
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(notification)

        return notification

    def delete(
        self,
        notification: Notification,
    ) -> None:
        """
        Delete a notification.
        """
        self.db.delete(notification)
        self.db.commit()

def create_refund_notification(
    self,
    user_id: int,
    event_name: str,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title="Event Cancelled - Ticket Refunded",
        message=(
            f"Your ticket for '{event_name}' has been refunded because "
            "the event was cancelled."
        ),
        notification_type=NotificationType.REFUND,
    )

    self.db.add(notification)
    self.db.commit()
    self.db.refresh(notification)

    return notification