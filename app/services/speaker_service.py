from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.speaker import Speaker
from app.repositories.speaker_repository import SpeakerRepository
from app.schemas.speaker import SpeakerCreate, SpeakerUpdate


class SpeakerService:
    def __init__(self, db: Session):
        self.repository = SpeakerRepository(db)

    # -----------------------------
    # Create Speaker
    # -----------------------------

    def create_speaker(
        self,
        speaker_data: SpeakerCreate,
    ) -> Speaker:

        existing_speaker = self.repository.get_by_email(
            speaker_data.email
        )

        if existing_speaker:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Speaker with this email already exists",
            )

        speaker = Speaker(
            name=speaker_data.name,
            email=speaker_data.email,
            phone=speaker_data.phone,
            bio=speaker_data.bio,
            expertise=speaker_data.expertise,
            company=speaker_data.company,
            experience=speaker_data.experience,
            is_active=speaker_data.is_active,
        )

        return self.repository.create(speaker)

    # -----------------------------
    # Get All Speakers
    # -----------------------------

    def get_speakers(self) -> list[Speaker]:
        return self.repository.get_all()

    # -----------------------------
    # Get Speaker
    # -----------------------------

    def get_speaker(
        self,
        speaker_id: int,
    ) -> Speaker:

        speaker = self.repository.get_by_id(
            speaker_id
        )

        if not speaker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Speaker not found",
            )

        return speaker

    # -----------------------------
    # Update Speaker
    # -----------------------------

    def update_speaker(
        self,
        speaker_id: int,
        speaker_data: SpeakerUpdate,
    ) -> Speaker:

        speaker = self.get_speaker(speaker_id)

        update_data = speaker_data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return speaker

        # Check email uniqueness when email is being changed
        if "email" in update_data:
            existing_speaker = (
                self.repository.get_by_email(
                    update_data["email"]
                )
            )

            if (
                existing_speaker
                and existing_speaker.id != speaker.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Speaker with this email already exists",
                )

        return self.repository.update(
            speaker,
            update_data,
        )