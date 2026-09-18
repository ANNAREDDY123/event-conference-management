from datetime import datetime, timedelta


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
            "full_name": "Test User",
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


def event_payload():
    now = datetime.utcnow()

    return {
        "event_name": "Python Conference 2026",
        "description": "Annual Python technology conference",
        "event_type": "Conference",
        "start_date": (now + timedelta(days=10)).isoformat(),
        "end_date": (now + timedelta(days=11)).isoformat(),
        "registration_start": (now + timedelta(days=1)).isoformat(),
        "registration_end": (now + timedelta(days=9)).isoformat(),
        "capacity": 500,
        "status": "Draft",
    }


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_create_event_as_organizer(client):
    email = "organizer_create@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_name"] == "Python Conference 2026"
    assert data["event_type"] == "Conference"
    assert data["capacity"] == 500
    assert data["status"] == "Draft"


def test_attendee_cannot_create_event(client):
    email = "attendee_create@example.com"

    register_user(
        client,
        email,
        "Attendee",
    )

    token = login_user(client, email)

    response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_get_event(client):
    email = "organizer_get@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.get(
        f"/events/{event_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_get_events(client):
    email = "organizer_list@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    response = client.get(
        "/events",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert isinstance(events, list)
    assert len(events) >= 1


def test_filter_events_by_type(client):
    email = "organizer_filter@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    response = client.get(
        "/events?event_type=Conference",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) >= 1

    for event in events:
        assert event["event_type"] == "Conference"


def test_update_event_by_owner(client):
    email = "organizer_update@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.put(
        f"/events/{event_id}",
        json={
            "event_name": "Updated Python Conference 2026",
            "capacity": 600,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_name"] == "Updated Python Conference 2026"
    assert data["capacity"] == 600


def test_other_organizer_cannot_update_event(client):
    owner_email = "organizer_owner@example.com"
    other_email = "organizer_other@example.com"

    register_user(
        client,
        owner_email,
        "Event Organizer",
    )

    register_user(
        client,
        other_email,
        "Event Organizer",
    )

    owner_token = login_user(client, owner_email)
    other_token = login_user(client, other_email)

    create_response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(owner_token),
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.put(
        f"/events/{event_id}",
        json={
            "event_name": "Unauthorized Update",
        },
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


def test_invalid_event_dates(client):
    email = "organizer_invalid_dates@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    now = datetime.utcnow()

    payload = {
        "event_name": "Invalid Event",
        "description": "Invalid dates",
        "event_type": "Conference",
        "start_date": (now + timedelta(days=10)).isoformat(),
        "end_date": (now + timedelta(days=9)).isoformat(),
        "registration_start": (now + timedelta(days=1)).isoformat(),
        "registration_end": (now + timedelta(days=8)).isoformat(),
        "capacity": 100,
        "status": "Draft",
    }

    response = client.post(
        "/events",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_invalid_event_capacity(client):
    email = "organizer_invalid_capacity@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    payload = event_payload()
    payload["capacity"] = 0

    response = client.post(
        "/events",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_delete_event_by_owner(client):
    email = "organizer_delete@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_response = client.post(
        "/events",
        json=event_payload(),
        headers=auth_headers(token),
    )

    assert create_response.status_code == 201

    event_id = create_response.json()["id"]

    response = client.delete(
        f"/events/{event_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    response = client.get(
        f"/events/{event_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# Level 14 - Search, Filtering & Pagination
# ---------------------------------------------------------

def create_event_with_details(
    client,
    token,
    name,
    city,
    event_type="Conference",
    event_status="Draft",
    capacity=100,
):
    """
    Creates an Event.

    NOTE:
    The current Event model does not contain a city field.
    The city parameter is retained only for compatibility
    with existing test calls, but it is not sent to the
    Event API.
    """

    now = datetime.utcnow()

    payload = {
        "event_name": name,
        "description": f"{name} description",
        "event_type": event_type,
        "start_date": (now + timedelta(days=10)).isoformat(),
        "end_date": (now + timedelta(days=11)).isoformat(),
        "registration_start": (
            now + timedelta(days=1)
        ).isoformat(),
        "registration_end": (
            now + timedelta(days=9)
        ).isoformat(),
        "capacity": capacity,
        "status": event_status,
    }

    response = client.post(
        "/events",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    return response.json()


def test_search_events_by_name(client):
    email = "organizer_level14_search@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_event_with_details(
        client,
        token,
        "Python Developer Conference",
        "Hyderabad",
    )

    create_event_with_details(
        client,
        token,
        "Java Technology Summit",
        "Hyderabad",
    )

    response = client.get(
        "/events?search=Python",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) >= 1

    assert any(
        event["event_name"] == "Python Developer Conference"
        for event in events
    )


def test_filter_events_by_status(client):
    email = "organizer_level14_status@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_event_with_details(
        client,
        token,
        "Open Registration Event",
        "Hyderabad",
        event_status="Registration Open",
    )

    create_event_with_details(
        client,
        token,
        "Draft Event",
        "Hyderabad",
        event_status="Draft",
    )

    response = client.get(
        "/events?status=Registration%20Open",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) >= 1

    for event in events:
        assert event["status"] == "Registration Open"


def test_filter_events_by_type(client):
    email = "organizer_level14_type@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_event_with_details(
        client,
        token,
        "Conference Event",
        "Hyderabad",
        event_type="Conference",
    )

    create_event_with_details(
        client,
        token,
        "Workshop Event",
        "Hyderabad",
        event_type="Workshop",
    )

    response = client.get(
        "/events?event_type=Workshop",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) >= 1

    for event in events:
        assert event["event_type"] == "Workshop"


def test_paginate_events(client):
    email = "organizer_level14_pagination@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    for index in range(5):
        create_event_with_details(
            client,
            token,
            f"Pagination Event {index}",
            "Hyderabad",
        )

    response = client.get(
        "/events?page=1&page_size=2",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert isinstance(events, list)
    assert len(events) <= 2


def test_sort_events_by_start_date(client):
    email = "organizer_level14_sort@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    create_event_with_details(
        client,
        token,
        "Later Event",
        "Hyderabad",
    )

    create_event_with_details(
        client,
        token,
        "Earlier Event",
        "Hyderabad",
    )

    response = client.get(
        "/events?sort_by=start_date&sort_order=asc",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) >= 2

    dates = [
        datetime.fromisoformat(event["start_date"])
        for event in events
    ]

    assert dates == sorted(dates)


def test_invalid_event_pagination(client):
    email = "organizer_level14_invalid_page@example.com"

    register_user(
        client,
        email,
        "Event Organizer",
    )

    token = login_user(client, email)

    response = client.get(
        "/events?page=0&page_size=0",
        headers=auth_headers(token),
    )

    assert response.status_code == 422