from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venue import VenueStatus
from app.schemas.venue import (
    HallCreate,
    HallResponse,
    HallUpdate,
    VenueCreate,
    VenueResponse,
    VenueUpdate,
)
from app.services.venue_service import VenueService
from app.utils.dependencies import get_current_active_user


router = APIRouter(
    prefix="/venues",
    tags=["Venues"],
)


# =========================================================
# CREATE VENUE
# =========================================================

@router.post(
    "",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.create_venue(
        venue_data,
        current_user,
    )


# =========================================================
# GET ALL VENUES
# =========================================================

@router.get(
    "",
    response_model=list[VenueResponse],
)
def get_venues(
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    city: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    venue_status: VenueStatus | None = Query(
        default=None,
        alias="status",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="venue_name",
        pattern="^(venue_name|city|capacity|status)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.get_venues(
        search=search,
        city=city,
        status=venue_status,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# =========================================================
# GET SINGLE VENUE
# =========================================================

@router.get(
    "/{venue_id}",
    response_model=VenueResponse,
)
def get_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    venue = service.get_venue(venue_id)

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    return venue


# =========================================================
# UPDATE VENUE
# =========================================================

@router.put(
    "/{venue_id}",
    response_model=VenueResponse,
)
def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.update_venue(
        venue_id,
        venue_data,
        current_user,
    )


# =========================================================
# DELETE VENUE
# =========================================================

@router.delete(
    "/{venue_id}",
)
def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    service.delete_venue(
        venue_id,
        current_user,
    )

    return {
        "message": "Venue deleted successfully"
    }


# =========================================================
# CREATE HALL
# =========================================================

@router.post(
    "/{venue_id}/halls",
    response_model=HallResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hall(
    venue_id: int,
    hall_data: HallCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.create_hall(
        venue_id,
        hall_data,
        current_user,
    )


# =========================================================
# GET ALL HALLS FOR VENUE
# =========================================================

@router.get(
    "/{venue_id}/halls",
    response_model=list[HallResponse],
)
def get_halls_by_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.get_halls_by_venue(
        venue_id,
        current_user,
    )


# =========================================================
# GET SINGLE HALL
# =========================================================

@router.get(
    "/{venue_id}/halls/{hall_id}",
    response_model=HallResponse,
)
def get_hall(
    venue_id: int,
    hall_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    hall = service.get_hall(
        venue_id,
        hall_id,
        current_user,
    )

    if not hall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hall not found",
        )

    return hall


# =========================================================
# UPDATE HALL
# =========================================================

@router.put(
    "/{venue_id}/halls/{hall_id}",
    response_model=HallResponse,
)
def update_hall(
    venue_id: int,
    hall_id: int,
    hall_data: HallUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    return service.update_hall(
        venue_id,
        hall_id,
        hall_data,
        current_user,
    )


# =========================================================
# DELETE HALL
# =========================================================

@router.delete(
    "/{venue_id}/halls/{hall_id}",
)
def delete_hall(
    venue_id: int,
    hall_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = VenueService(db)

    service.delete_hall(
        venue_id,
        hall_id,
        current_user,
    )

    return {
        "message": "Hall deleted successfully"
    }