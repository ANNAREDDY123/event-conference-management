from fastapi import HTTPException, status

from app.models.event import EventStatus
from app.models.feedback import Feedback
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


class FeedbackService:
    def __init__(self, db):
        self.repository = FeedbackRepository(db)

    def create_feedback(
        self,
        feedback_data: FeedbackCreate,
    ) -> Feedback:
        # Validate attendee
        attendee = self.repository.get_attendee(
            feedback_data.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        # Validate event
        event = self.repository.get_event(
            feedback_data.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Ensure attendee belongs to the event
        if attendee.event_id != event.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendee is not registered for this event",
            )

        # Feedback can only be submitted after event completion
        if event.status != EventStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback can only be submitted for a completed event",
            )

        # Prevent duplicate feedback
        existing_feedback = self.repository.get_existing_feedback(
            attendee_id=feedback_data.attendee_id,
            event_id=feedback_data.event_id,
        )

        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Feedback already exists for this attendee and event",
            )

        feedback = Feedback(
            attendee_id=feedback_data.attendee_id,
            event_id=feedback_data.event_id,
            rating=feedback_data.rating,
            comments=feedback_data.comments,
        )

        return self.repository.create(feedback)

    def get_feedback(
        self,
        feedback_id: int,
    ) -> Feedback:
        feedback = self.repository.get_by_id(feedback_id)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found",
            )

        return feedback

    def get_feedbacks(self) -> list[Feedback]:
        return self.repository.get_all()

    def get_feedbacks_by_attendee(
        self,
        attendee_id: int,
    ) -> list[Feedback]:
        attendee = self.repository.get_attendee(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return self.repository.get_by_attendee(
            attendee_id
        )

    def get_feedbacks_by_event(
        self,
        event_id: int,
    ) -> list[Feedback]:
        event = self.repository.get_event(
            event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return self.repository.get_by_event(
            event_id
        )

    def update_feedback(
        self,
        feedback_id: int,
        feedback_data: FeedbackUpdate,
    ) -> Feedback:
        feedback = self.repository.get_by_id(feedback_id)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found",
            )

        if feedback_data.rating is not None:
            feedback.rating = feedback_data.rating

        if feedback_data.comments is not None:
            feedback.comments = feedback_data.comments

        return self.repository.update(feedback)

    def delete_feedback(
        self,
        feedback_id: int,
    ) -> None:
        feedback = self.repository.get_by_id(feedback_id)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found",
            )

        self.repository.delete(feedback)