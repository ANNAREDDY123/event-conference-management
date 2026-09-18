# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def register_user(client, email: str, role: str = "Attendee"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Attendee Test User",
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


def create_event(client, token: str, organizer_id: int, capacity: int = 100):
    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": "Attendee Test Event",
            "description": "Event for attendee testing",
            "event_type": "Conference",
            "organizer_id": organizer_id,
            "start_date": "2026-11-10T09:00:00",
            "end_date": "2026-11-10T18:00:00",
            "registration_start": "2026-10-01T09:00:00",
            "registration_end": "2026-11-09T18:00:00",
            "capacity": capacity,
            "status": "Registration Open",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def setup_event(client, user_email: str, capacity: int = 100):
    user = register_user(
        client,
        user_email,
        "Event Organizer",
    )

    token = login_user(
        client,
        user_email,
    )

    event_id = create_event(
        client,
        token,
        user["id"],
        capacity,
    )

    return token, event_id


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_register_attendee(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_register@example.com",
    )

    response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == attendee["id"]
    assert data["event_id"] == event_id
    assert data["status"] == "Registered"
    assert "registration_date" in data


def test_get_attendee(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_get_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_get@example.com",
    )

    create_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert create_response.status_code == 201

    attendee_id = create_response.json()["id"]

    response = client.get(
        f"/attendees/{attendee_id}",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == attendee_id


def test_get_attendees(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_list_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_list@example.com",
    )

    create_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/attendees",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_attendees_by_event(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_event_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_event@example.com",
    )

    create_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/attendees/event/{event_id}",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["event_id"] == event_id


def test_duplicate_attendee_registration(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_duplicate_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_duplicate@example.com",
    )

    payload = {
        "user_id": attendee["id"],
        "event_id": event_id,
    }

    first_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json=payload,
    )

    assert first_response.status_code == 201

    response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json=payload,
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Attendee is already registered for this event"
    )


def test_nonexistent_user(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_invalid_user_organizer@example.com",
    )

    response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": 999999,
            "event_id": event_id,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_nonexistent_event(client):
    organizer_token, _ = setup_event(
        client,
        "attendee_invalid_event_organizer@example.com",
    )

    attendee = register_user(
        client,
        "attendee_invalid_event@example.com",
    )

    response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_event_registration_capacity_full(client):
    organizer_token, event_id = setup_event(
        client,
        "attendee_capacity_organizer@example.com",
        capacity=1,
    )

    first_attendee = register_user(
        client,
        "attendee_capacity_one@example.com",
    )

    second_attendee = register_user(
        client,
        "attendee_capacity_two@example.com",
    )

    first_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": first_attendee["id"],
            "event_id": event_id,
        },
    )

    assert first_response.status_code == 201

    response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": second_attendee["id"],
            "event_id": event_id,
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Event registration capacity is full"
    )


def test_get_nonexistent_attendee(client):
    organizer_token, _ = setup_event(
        client,
        "attendee_not_found_organizer@example.com",
    )

    response = client.get(
        "/attendees/999999",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attendee not found"


def test_get_attendees_nonexistent_event(client):
    organizer_token, _ = setup_event(
        client,
        "attendee_event_not_found_organizer@example.com",
    )

    response = client.get(
        "/attendees/event/999999",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"