# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def register_user(client, email: str, role: str = "Event Organizer"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Session Test User",
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
    return {"Authorization": f"Bearer {token}"}


def create_event(client, token: str, organizer_id: int):
    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": "Session Test Event",
            "description": "Event for session testing",
            "event_type": "Conference",
            "organizer_id": organizer_id,
            "start_date": "2026-10-10T09:00:00",
            "end_date": "2026-10-10T18:00:00",
            "registration_start": "2026-09-20T09:00:00",
            "registration_end": "2026-10-09T18:00:00",
            "capacity": 500,
            "status": "Draft",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_venue(client, token: str):
    response = client.post(
        "/venues",
        headers=auth_headers(token),
        json={
            "venue_name": "Session Test Venue",
            "address": "HITEC City, Hyderabad",
            "city": "Hyderabad",
            "capacity": 500,
            "facilities": "WiFi, AC, Projector",
            "status": "Active",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_hall(
    client,
    token: str,
    venue_id: int,
    name: str,
    capacity: int = 300,
):
    response = client.post(
        f"/venues/{venue_id}/halls",
        headers=auth_headers(token),
        json={
            "hall_name": name,
            "capacity": capacity,
            "floor": 1,
            "availability_status": "Available",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_speaker(client, token: str, email: str):
    response = client.post(
        "/speakers",
        headers=auth_headers(token),
        json={
            "name": "Session Test Speaker",
            "email": email,
            "phone": "9876543210",
            "bio": "Speaker for session testing",
            "expertise": "Python, FastAPI",
            "company": "Test Company",
            "experience": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def session_payload(
    event_id: int,
    hall_id: int,
    speaker_id: int | None = None,
    title: str = "FastAPI Session",
    start_time: str = "2026-10-10T10:00:00",
    end_time: str = "2026-10-10T11:00:00",
    capacity: int = 200,
):
    return {
        "event_id": event_id,
        "speaker_id": speaker_id,
        "hall_id": hall_id,
        "title": title,
        "description": "Session testing",
        "session_type": "Technical",
        "start_time": start_time,
        "end_time": end_time,
        "capacity": capacity,
        "status": "Scheduled",
    }


def setup_session_data(
    client,
    user_email: str,
    speaker_email: str | None = None,
):
    user = register_user(client, user_email)
    token = login_user(client, user_email)

    organizer_id = user["id"]

    event_id = create_event(
        client,
        token,
        organizer_id,
    )

    venue_id = create_venue(
        client,
        token,
    )

    hall_id = create_hall(
        client,
        token,
        venue_id,
        "Main Hall",
    )

    speaker_id = None

    if speaker_email:
        speaker_id = create_speaker(
            client,
            token,
            speaker_email,
        )

    return token, event_id, venue_id, hall_id, speaker_id


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_create_session(client):
    token, event_id, _, hall_id, speaker_id = setup_session_data(
        client,
        "session_create_user@example.com",
        "session_create_speaker@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            speaker_id,
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_id"] == event_id
    assert data["hall_id"] == hall_id
    assert data["speaker_id"] == speaker_id
    assert data["title"] == "FastAPI Session"
    assert data["capacity"] == 200


def test_get_sessions(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_list_user@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
        ),
    )

    assert response.status_code == 201

    response = client.get(
        "/sessions",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    sessions = response.json()

    assert isinstance(sessions, list)
    assert len(sessions) >= 1


def test_get_session(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_get_user@example.com",
    )

    create_response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
        ),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["id"]

    response = client.get(
        f"/sessions/{session_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_get_sessions_by_event(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_event_user@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
        ),
    )

    assert response.status_code == 201

    response = client.get(
        f"/sessions/event/{event_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_session(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_update_user@example.com",
    )

    create_response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
        ),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["id"]

    response = client.put(
        f"/sessions/{session_id}",
        headers=auth_headers(token),
        json={
            "title": "Updated Session",
            "capacity": 250,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Session"
    assert response.json()["capacity"] == 250


def test_invalid_session_time(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_invalid_time@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            start_time="2026-10-10T12:00:00",
            end_time="2026-10-10T11:00:00",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Session end time must be after start time"
    )


def test_session_outside_event_time(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_outside_event@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            start_time="2026-10-10T17:30:00",
            end_time="2026-10-10T19:00:00",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Session must be within event start and end time"
    )


def test_session_capacity_cannot_exceed_hall(client):
    token, event_id, venue_id, _, _ = setup_session_data(
        client,
        "session_capacity@example.com",
    )

    small_hall_id = create_hall(
        client,
        token,
        venue_id,
        "Small Hall",
        capacity=100,
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            small_hall_id,
            capacity=200,
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Session capacity cannot exceed hall capacity"
    )


def test_hall_double_booking(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_hall_conflict@example.com",
    )

    first_response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            start_time="2026-10-10T10:00:00",
            end_time="2026-10-10T11:00:00",
        ),
    )

    assert first_response.status_code == 201

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            title="Hall Conflict",
            start_time="2026-10-10T10:30:00",
            end_time="2026-10-10T11:30:00",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Hall is already booked for an overlapping session"
    )


def test_speaker_double_booking(client):
    token, event_id, venue_id, hall_one, speaker_id = setup_session_data(
        client,
        "session_speaker_conflict@example.com",
        "speaker.conflict@example.com",
    )

    hall_two = create_hall(
        client,
        token,
        venue_id,
        "Speaker Hall Two",
    )

    first_response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_one,
            speaker_id,
            start_time="2026-10-10T10:00:00",
            end_time="2026-10-10T11:00:00",
        ),
    )

    assert first_response.status_code == 201

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_two,
            speaker_id,
            title="Speaker Conflict",
            start_time="2026-10-10T10:30:00",
            end_time="2026-10-10T11:30:00",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Speaker is already assigned to an overlapping session"
    )


def test_inactive_speaker_cannot_be_assigned(client):
    token, event_id, _, hall_id, speaker_id = setup_session_data(
        client,
        "session_inactive_speaker@example.com",
        "inactive.session.speaker@example.com",
    )

    deactivate_response = client.put(
        f"/speakers/{speaker_id}",
        headers=auth_headers(token),
        json={
            "is_active": False
        },
    )

    assert deactivate_response.status_code == 200

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            speaker_id,
            start_time="2026-10-10T12:00:00",
            end_time="2026-10-10T13:00:00",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Inactive speaker cannot be assigned to a session"
    )


def test_nonexistent_event(client):
    token, _, _, hall_id, _ = setup_session_data(
        client,
        "session_invalid_event@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            999999,
            hall_id,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_nonexistent_speaker(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_invalid_speaker@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
            speaker_id=999999,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Speaker not found"


def test_nonexistent_hall(client):
    token, event_id, _, _, _ = setup_session_data(
        client,
        "session_invalid_hall@example.com",
    )

    response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            999999,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Hall not found"


def test_get_nonexistent_session(client):
    token, _, _, _, _ = setup_session_data(
        client,
        "session_not_found@example.com",
    )

    response = client.get(
        "/sessions/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_delete_session(client):
    token, event_id, _, hall_id, _ = setup_session_data(
        client,
        "session_delete@example.com",
    )

    create_response = client.post(
        "/sessions",
        headers=auth_headers(token),
        json=session_payload(
            event_id,
            hall_id,
        ),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["id"]

    response = client.delete(
        f"/sessions/{session_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    response = client.get(
        f"/sessions/{session_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 404