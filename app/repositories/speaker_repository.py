from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.speaker import Speaker


class SpeakerRepository:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # Speaker Operations
    # -----------------------------

    def create(self, speaker: Speaker) -> Speaker:
        self.db.add(speaker)
        self.db.commit()
        self.db.refresh(speaker)

        return speaker

    def get_by_id(self, speaker_id: int) -> Speaker | None:
        statement = select(Speaker).where(
            Speaker.id == speaker_id
        )

        return self.db.scalar(statement)

    def get_by_email(self, email: str) -> Speaker | None:
        statement = select(Speaker).where(
            Speaker.email == email
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[Speaker]:
        statement = select(Speaker).order_by(
            Speaker.name
        )

        return list(
            self.db.scalars(statement).all()
        )

    def update(
        self,
        speaker: Speaker,
        update_data: dict,
    ) -> Speaker:

        for field, value in update_data.items():
            setattr(speaker, field, value)

        self.db.commit()
        self.db.refresh(speaker)

        return speaker