from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services.session_service import SessionService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    return service.create_session(session_data)


@router.get(
    "",
    response_model=list[SessionResponse],
)
def get_sessions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    return service.get_sessions()


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    return service.get_session(session_id)


@router.get(
    "/event/{event_id}",
    response_model=list[SessionResponse],
)
def get_sessions_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    return service.get_sessions_by_event(event_id)


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    return service.update_session(
        session_id,
        session_data,
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SessionService(db)

    service.delete_session(session_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)