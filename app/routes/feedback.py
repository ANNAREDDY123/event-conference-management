from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackUpdate,
)
from app.services.feedback_service import FeedbackService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).create_feedback(feedback_data)


@router.get(
    "",
    response_model=list[FeedbackResponse],
)
def get_feedbacks(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).get_feedbacks()


@router.get(
    "/attendee/{attendee_id}",
    response_model=list[FeedbackResponse],
)
def get_feedbacks_by_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).get_feedbacks_by_attendee(
        attendee_id
    )


@router.get(
    "/event/{event_id}",
    response_model=list[FeedbackResponse],
)
def get_feedbacks_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).get_feedbacks_by_event(
        event_id
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).get_feedback(feedback_id)


@router.put(
    "/{feedback_id}",
    response_model=FeedbackResponse,
)
def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return FeedbackService(db).update_feedback(
        feedback_id,
        feedback_data,
    )


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    FeedbackService(db).delete_feedback(feedback_id)