from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app as fastapi_app


# ---------------------------------------------------------
# Test database setup
# ---------------------------------------------------------

import app.models


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def register_user(
    client,
    email: str,
    role: str = "Attendee",
):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Venue Test User",
            "email": email,
            "password": "TestPassword123",
            "role": role,
        },
    )

    assert response.status_code == 201
    return response.json()


def login_user(client, email: str):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
    }


# =========================================================
# LEVEL 3 - VENUE TESTS
# =========================================================


def test_create_venue(client):
    email = "venue_create@example.com"

    register_user(client, email)

    token = login_user(client, email)

    response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Grand Convention Center",
            "address": "HITEC City, Hyderabad",
            "city": "Hyderabad",
            "capacity": 1000,
            "facilities": "WiFi, AC, Parking, Projector",
            "status": "Active",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["venue_name"] == "Grand Convention Center"
    assert data["city"] == "Hyderabad"
    assert data["capacity"] == 1000
    assert data["status"] == "Active"


def test_get_venues(client):
    email = "venue_list@example.com"

    register_user(client, email)

    token = login_user(client, email)

    create_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "List Test Venue",
            "address": "Madhapur, Hyderabad",
            "city": "Hyderabad",
            "capacity": 500,
            "facilities": "WiFi, AC",
            "status": "Active",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/venues",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert isinstance(venues, list)
    assert len(venues) >= 1


def test_get_venue(client):
    email = "venue_get@example.com"

    register_user(client, email)

    token = login_user(client, email)

    create_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Get Test Venue",
            "address": "Gachibowli, Hyderabad",
            "city": "Hyderabad",
            "capacity": 400,
            "facilities": "WiFi",
            "status": "Active",
        },
    )

    assert create_response.status_code == 201

    venue_id = create_response.json()["id"]

    response = client.get(
        f"/venues/{venue_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == venue_id
    assert data["venue_name"] == "Get Test Venue"


def test_create_hall(client):
    email = "hall_create@example.com"

    register_user(client, email)

    token = login_user(client, email)

    venue_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Hall Test Venue",
            "address": "Kondapur, Hyderabad",
            "city": "Hyderabad",
            "capacity": 500,
            "facilities": "WiFi, AC",
            "status": "Active",
        },
    )

    assert venue_response.status_code == 201

    venue_id = venue_response.json()["id"]

    response = client.post(
        f"/venues/{venue_id}/halls",
        headers=auth_headers(token),
        json={
            "hall_name": "Main Hall",
            "capacity": 300,
            "floor": 1,
            "availability_status": "Available",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["venue_id"] == venue_id
    assert data["hall_name"] == "Main Hall"
    assert data["capacity"] == 300
    assert data["floor"] == 1
    assert data["availability_status"] == "Available"


def test_get_hall(client):
    email = "hall_get@example.com"

    register_user(client, email)

    token = login_user(client, email)

    venue_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Hall Get Venue",
            "address": "Banjara Hills, Hyderabad",
            "city": "Hyderabad",
            "capacity": 600,
            "facilities": "WiFi, Parking",
            "status": "Active",
        },
    )

    assert venue_response.status_code == 201

    venue_id = venue_response.json()["id"]

    hall_response = client.post(
        f"/venues/{venue_id}/halls",
        headers=auth_headers(token),
        json={
            "hall_name": "Get Hall",
            "capacity": 300,
            "floor": 2,
            "availability_status": "Available",
        },
    )

    assert hall_response.status_code == 201

    hall_id = hall_response.json()["id"]

    response = client.get(
        f"/venues/{venue_id}/halls/{hall_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == hall_id
    assert data["venue_id"] == venue_id


def test_get_halls_by_venue(client):
    email = "hall_list@example.com"

    register_user(client, email)

    token = login_user(client, email)

    venue_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Hall List Venue",
            "address": "Secunderabad, Hyderabad",
            "city": "Hyderabad",
            "capacity": 1000,
            "facilities": "WiFi, AC",
            "status": "Active",
        },
    )

    assert venue_response.status_code == 201

    venue_id = venue_response.json()["id"]

    for hall_name in ["Hall One", "Hall Two"]:
        response = client.post(
            f"/venues/{venue_id}/halls",
            headers=auth_headers(token),
            json={
                "hall_name": hall_name,
                "capacity": 300,
                "floor": 1,
                "availability_status": "Available",
            },
        )

        assert response.status_code == 201

    response = client.get(
        f"/venues/{venue_id}/halls",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    halls = response.json()

    assert isinstance(halls, list)
    assert len(halls) >= 2


def test_hall_capacity_cannot_exceed_venue_capacity(client):
    email = "hall_capacity@example.com"

    register_user(client, email)

    token = login_user(client, email)

    venue_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Small Venue",
            "address": "Miyapur, Hyderabad",
            "city": "Hyderabad",
            "capacity": 100,
            "facilities": "WiFi",
            "status": "Active",
        },
    )

    assert venue_response.status_code == 201

    venue_id = venue_response.json()["id"]

    response = client.post(
        f"/venues/{venue_id}/halls",
        headers=auth_headers(token),
        json={
            "hall_name": "Too Large Hall",
            "capacity": 200,
            "floor": 1,
            "availability_status": "Available",
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Hall capacity cannot exceed venue capacity"
    )


def test_nonexistent_venue(client):
    email = "venue_not_found@example.com"

    register_user(client, email)

    token = login_user(client, email)

    response = client.get(
        "/venues/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_nonexistent_hall(client):
    email = "hall_not_found@example.com"

    register_user(client, email)

    token = login_user(client, email)

    venue_response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Not Found Hall Venue",
            "address": "Kukatpally, Hyderabad",
            "city": "Hyderabad",
            "capacity": 500,
            "facilities": "WiFi",
            "status": "Active",
        },
    )

    assert venue_response.status_code == 201

    venue_id = venue_response.json()["id"]

    response = client.get(
        f"/venues/{venue_id}/halls/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_get_halls_for_nonexistent_venue(client):
    email = "venue_halls_not_found@example.com"

    register_user(client, email)

    token = login_user(client, email)

    response = client.get(
        "/venues/999999/halls",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


# =========================================================
# LEVEL 14
# SEARCH / FILTERING / PAGINATION / SORTING
# =========================================================


def create_level14_venue(
    client,
    token,
    name,
    city,
    capacity=500,
    venue_status="Active",
    facilities="WiFi, AC, Projector",
):
    response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": name,
            "address": f"Main Road, {city}",
            "city": city,
            "capacity": capacity,
            "facilities": facilities,
            "status": venue_status,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_search_venues(client):
    email = "venue_level14_search@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_level14_venue(
        client,
        token,
        "Hyderabad Convention Center",
        "Hyderabad",
    )

    create_level14_venue(
        client,
        token,
        "Bangalore Tech Hall",
        "Bangalore",
    )

    response = client.get(
        "/venues?search=Convention",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert len(venues) >= 1

    assert any(
        venue["venue_name"] == "Hyderabad Convention Center"
        for venue in venues
    )


def test_filter_venues_by_city(client):
    email = "venue_level14_city@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_level14_venue(
        client,
        token,
        "Hyderabad Venue One",
        "Hyderabad",
    )

    create_level14_venue(
        client,
        token,
        "Bangalore Venue One",
        "Bangalore",
    )

    response = client.get(
        "/venues?city=Hyderabad",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert len(venues) >= 1

    for venue in venues:
        assert venue["city"].lower() == "hyderabad"


def test_filter_venues_by_status(client):
    email = "venue_level14_status@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_level14_venue(
        client,
        token,
        "Active Venue",
        "Hyderabad",
        venue_status="Active",
    )

    create_level14_venue(
        client,
        token,
        "Inactive Venue",
        "Hyderabad",
        venue_status="Inactive",
    )

    response = client.get(
        "/venues?status=Active",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert len(venues) >= 1

    for venue in venues:
        assert venue["status"] == "Active"


def test_paginate_venues(client):
    email = "venue_level14_pagination@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    for index in range(5):
        create_level14_venue(
            client,
            token,
            f"Pagination Venue {index}",
            "Hyderabad",
        )

    response = client.get(
        "/venues?page=1&page_size=2",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert isinstance(venues, list)
    assert len(venues) <= 2


def test_second_page_venues(client):
    email = "venue_level14_second_page@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    for index in range(5):
        create_level14_venue(
            client,
            token,
            f"Second Page Venue {index}",
            "Hyderabad",
        )

    first_response = client.get(
        "/venues?page=1&page_size=2",
        headers=auth_headers(token),
    )

    second_response = client.get(
        "/venues?page=2&page_size=2",
        headers=auth_headers(token),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_page = first_response.json()
    second_page = second_response.json()

    assert len(first_page) <= 2
    assert len(second_page) <= 2

    first_ids = {
        venue["id"]
        for venue in first_page
    }

    second_ids = {
        venue["id"]
        for venue in second_page
    }

    assert first_ids.isdisjoint(second_ids)


def test_sort_venues_by_name_ascending(client):
    email = "venue_level14_sort_asc@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_level14_venue(
        client,
        token,
        "Zeta Convention Hall",
        "Hyderabad",
    )

    create_level14_venue(
        client,
        token,
        "Alpha Convention Hall",
        "Hyderabad",
    )

    response = client.get(
        "/venues?sort_by=venue_name&sort_order=asc",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert len(venues) >= 2

    names = [
        venue["venue_name"]
        for venue in venues
    ]

    assert names == sorted(names)


def test_sort_venues_by_capacity_descending(client):
    email = "venue_level14_sort_desc@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_level14_venue(
        client,
        token,
        "Small Venue",
        "Hyderabad",
        capacity=100,
    )

    create_level14_venue(
        client,
        token,
        "Large Venue",
        "Hyderabad",
        capacity=1000,
    )

    response = client.get(
        "/venues?sort_by=capacity&sort_order=desc",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    venues = response.json()

    assert len(venues) >= 2

    capacities = [
        venue["capacity"]
        for venue in venues
    ]

    assert capacities == sorted(
        capacities,
        reverse=True,
    )


def test_invalid_venue_pagination(client):
    email = "venue_level14_invalid_page@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.get(
        "/venues?page=0&page_size=0",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_invalid_venue_sort_field(client):
    email = "venue_level14_invalid_sort@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.get(
        "/venues?sort_by=invalid_field",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_invalid_venue_sort_order(client):
    email = "venue_level14_invalid_order@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.get(
        "/venues?sort_order=random",
        headers=auth_headers(token),
    )

    assert response.status_code == 422