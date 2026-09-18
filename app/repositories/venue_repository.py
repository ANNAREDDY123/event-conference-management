from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.venue import Hall, Venue


class VenueRepository:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # VENUE - CREATE
    # =========================================================

    def create_venue(self, venue_data):
        venue = Venue(
            venue_name=venue_data.venue_name,
            address=venue_data.address,
            city=venue_data.city,
            capacity=venue_data.capacity,
            facilities=venue_data.facilities,
            status=venue_data.status,
        )

        self.db.add(venue)
        self.db.commit()
        self.db.refresh(venue)

        return venue

    # =========================================================
    # VENUE - GET ALL
    # =========================================================

    def get_all(
        self,
        search: str | None = None,
        city: str | None = None,
        status=None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "venue_name",
        sort_order: str = "asc",
    ):
        query = self.db.query(Venue)

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    Venue.venue_name.ilike(search_value),
                    Venue.address.ilike(search_value),
                    Venue.city.ilike(search_value),
                    Venue.facilities.ilike(search_value),
                )
            )

        # -----------------------------------------------------
        # City filter
        # -----------------------------------------------------

        if city:
            query = query.filter(
                Venue.city.ilike(f"%{city}%")
            )

        # -----------------------------------------------------
        # Status filter
        # -----------------------------------------------------

        if status is not None:
            query = query.filter(
                Venue.status == status
            )

        # -----------------------------------------------------
        # Sorting
        # -----------------------------------------------------

        allowed_sort_fields = {
            "venue_name": Venue.venue_name,
            "city": Venue.city,
            "capacity": Venue.capacity,
            "status": Venue.status,
        }

        sort_column = allowed_sort_fields.get(
            sort_by,
            Venue.venue_name,
        )

        if sort_order.lower() == "desc":
            query = query.order_by(
                desc(sort_column)
            )
        else:
            query = query.order_by(
                asc(sort_column)
            )

        # -----------------------------------------------------
        # Pagination
        # -----------------------------------------------------

        offset = (page - 1) * page_size

        return (
            query
            .offset(offset)
            .limit(page_size)
            .all()
        )

    # =========================================================
    # VENUE - GET BY ID
    # =========================================================

    def get_by_id(self, venue_id: int):
        return (
            self.db.query(Venue)
            .filter(Venue.id == venue_id)
            .first()
        )

    # =========================================================
    # VENUE - UPDATE
    # =========================================================

    def update_venue(
        self,
        venue_id: int,
        venue_data,
    ):
        venue = self.get_by_id(venue_id)

        if not venue:
            return None

        update_data = venue_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(venue, field, value)

        self.db.commit()
        self.db.refresh(venue)

        return venue

    # =========================================================
    # VENUE - DELETE
    # =========================================================

    def delete_venue(self, venue_id: int):
        venue = self.get_by_id(venue_id)

        if not venue:
            return None

        self.db.delete(venue)
        self.db.commit()

        return venue

    # =========================================================
    # HALL - CREATE
    # =========================================================

    def create_hall(
        self,
        venue_id: int,
        hall_data,
    ):
        hall = Hall(
            venue_id=venue_id,
            hall_name=hall_data.hall_name,
            capacity=hall_data.capacity,
            floor=hall_data.floor,
            availability_status=hall_data.availability_status,
        )

        self.db.add(hall)
        self.db.commit()
        self.db.refresh(hall)

        return hall

    # =========================================================
    # HALL - GET ALL BY VENUE
    # =========================================================

    def get_halls_by_venue(
        self,
        venue_id: int,
    ):
        return (
            self.db.query(Hall)
            .filter(Hall.venue_id == venue_id)
            .order_by(Hall.id)
            .all()
        )

    # =========================================================
    # HALL - GET SINGLE
    # =========================================================

    def get_hall(
        self,
        venue_id: int,
        hall_id: int,
    ):
        return (
            self.db.query(Hall)
            .filter(
                Hall.id == hall_id,
                Hall.venue_id == venue_id,
            )
            .first()
        )

    # =========================================================
    # HALL - UPDATE
    # =========================================================

    def update_hall(
        self,
        venue_id: int,
        hall_id: int,
        hall_data,
    ):
        hall = self.get_hall(
            venue_id,
            hall_id,
        )

        if not hall:
            return None

        update_data = hall_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(hall, field, value)

        self.db.commit()
        self.db.refresh(hall)

        return hall

    # =========================================================
    # HALL - DELETE
    # =========================================================

    def delete_hall(
        self,
        venue_id: int,
        hall_id: int,
    ):
        hall = self.get_hall(
            venue_id,
            hall_id,
        )

        if not hall:
            return None

        self.db.delete(hall)
        self.db.commit()

        return hall