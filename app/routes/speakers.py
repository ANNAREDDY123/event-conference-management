from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.speaker import (
    SpeakerCreate,
    SpeakerResponse,
    SpeakerUpdate,
)
from app.services.speaker_service import SpeakerService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/speakers",
    tags=["Speakers"],
)


@router.post(
    "",
    response_model=SpeakerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_speaker(
    speaker_data: SpeakerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SpeakerService(db)

    return service.create_speaker(
        speaker_data
    )


@router.get(
    "",
    response_model=list[SpeakerResponse],
)
def get_speakers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SpeakerService(db)

    return service.get_speakers()


@router.get(
    "/{speaker_id}",
    response_model=SpeakerResponse,
)
def get_speaker(
    speaker_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SpeakerService(db)

    return service.get_speaker(
        speaker_id
    )


@router.put(
    "/{speaker_id}",
    response_model=SpeakerResponse,
)
def update_speaker(
    speaker_id: int,
    speaker_data: SpeakerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SpeakerService(db)

    return service.update_speaker(
        speaker_id,
        speaker_data,
    )