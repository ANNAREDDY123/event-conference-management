from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationStatus, NotificationType


class NotificationCreate(BaseModel):
    user_id: int = Field(gt=0)
    title: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=1)
    notification_type: NotificationType


class NotificationUpdate(BaseModel):
    status: NotificationStatus | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    status: NotificationStatus
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)