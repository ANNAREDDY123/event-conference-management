from fastapi import HTTPException, status

from app.models.venue import VenueStatus
from app.repositories.venue_repository import VenueRepository


class VenueService:

    def __init__(self, db):
        self.repository = VenueRepository(db)

    # =========================================================
    # CREATE VENUE
    # =========================================================

    def create_venue(
        self,
        venue_data,
        current_user=None,
    ):
        if venue_data.capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Venue capacity must be greater than 0",
            )

        return self.repository.create_venue(
            venue_data
        )

    # =========================================================
    # GET ALL VENUES
    # =========================================================

    def get_venues(
        self,
        search: str | None = None,
        city: str | None = None,
        status: VenueStatus | None = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "venue_name",
        sort_order: str = "asc",
    ):
        return self.repository.get_all(
            search=search,
            city=city,
            status=status,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # =========================================================
    # GET SINGLE VENUE
    # =========================================================

    def get_venue(
        self,
        venue_id: int,
    ):
        return self.repository.get_by_id(
            venue_id
        )

    # =========================================================
    # UPDATE VENUE
    # =========================================================

    def update_venue(
        self,
        venue_id: int,
        venue_data,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        if venue_data.capacity is not None:

            if venue_data.capacity <= 0:
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_ENTITY
                    ),
                    detail=(
                        "Venue capacity must be "
                        "greater than 0"
                    ),
                )

            halls = self.repository.get_halls_by_venue(
                venue_id
            )

            for hall in halls:
                if hall.capacity > venue_data.capacity:
                    raise HTTPException(
                        status_code=(
                            status.HTTP_422_UNPROCESSABLE_ENTITY
                        ),
                        detail=(
                            "Venue capacity cannot be "
                            "less than existing hall "
                            "capacity"
                        ),
                    )

        return self.repository.update_venue(
            venue_id,
            venue_data,
        )

    # =========================================================
    # DELETE VENUE
    # =========================================================

    def delete_venue(
        self,
        venue_id: int,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        self.repository.delete_venue(
            venue_id
        )

        return venue

    # =========================================================
    # CREATE HALL
    # =========================================================

    def create_hall(
        self,
        venue_id: int,
        hall_data,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        if hall_data.capacity > venue.capacity:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Hall capacity cannot exceed "
                    "venue capacity"
                ),
            )

        return self.repository.create_hall(
            venue_id,
            hall_data,
        )

    # =========================================================
    # GET ALL HALLS FOR VENUE
    # =========================================================

    def get_halls_by_venue(
        self,
        venue_id: int,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        return self.repository.get_halls_by_venue(
            venue_id
        )

    # =========================================================
    # GET SINGLE HALL
    # =========================================================

    def get_hall(
        self,
        venue_id: int,
        hall_id: int,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        return self.repository.get_hall(
            venue_id,
            hall_id,
        )

    # =========================================================
    # UPDATE HALL
    # =========================================================

    def update_hall(
        self,
        venue_id: int,
        hall_id: int,
        hall_data,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        hall = self.repository.get_hall(
            venue_id,
            hall_id,
        )

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall not found",
            )

        if (
            hall_data.capacity is not None
            and hall_data.capacity > venue.capacity
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Hall capacity cannot exceed "
                    "venue capacity"
                ),
            )

        return self.repository.update_hall(
            venue_id,
            hall_id,
            hall_data,
        )

    # =========================================================
    # DELETE HALL
    # =========================================================

    def delete_hall(
        self,
        venue_id: int,
        hall_id: int,
        current_user=None,
    ):
        venue = self.repository.get_by_id(
            venue_id
        )

        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found",
            )

        hall = self.repository.get_hall(
            venue_id,
            hall_id,
        )

        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall not found",
            )

        self.repository.delete_hall(
            venue_id,
            hall_id,
        )

        return hall