from datetime import datetime, timedelta

from app.models.check_in import CheckInStatus
from app.models.event import EventStatus


def create_user(client, email="checkin@example.com"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Check In User",
            "email": email,
            "password": "Test@123",
            "role": "Attendee",
        },
    )
    assert response.status_code == 201
    return response.json()


def login(client, email="checkin@example.com"):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_organizer(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Event Organizer",
            "email": "organizer_checkin@example.com",
            "password": "Test@123",
            "role": "Event Organizer",
        },
    )
    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "organizer_checkin@example.com",
            "password": "Test@123",
        },
    )
    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def create_event(client, token):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": "Check-In Conference",
            "description": "Check-In Test Event",
            "event_type": "Conference",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=2)).isoformat(),
            "registration_start": (now - timedelta(days=1)).isoformat(),
            "registration_end": (now + timedelta(hours=12)).isoformat(),
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_attendee(client, token, event_id, email="attendee_checkin@example.com"):
    user_response = client.post(
        "/auth/register",
        json={
            "full_name": "Event Attendee",
            "email": email,
            "password": "Test@123",
            "role": "Attendee",
        },
    )
    assert user_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )
    assert login_response.status_code == 200

    attendee_token = login_response.json()["access_token"]

    response = client.post(
        "/attendees",
        headers=auth_headers(attendee_token),
        json={
            "user_id": user_response.json()["id"],
            "event_id": event_id,
        },
    )

    assert response.status_code == 201
    return response.json(), attendee_token


def test_create_check_in(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
    )

    response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["attendee_id"] == attendee["id"]
    assert data["event_id"] == event["id"]
    assert data["status"] == CheckInStatus.CHECKED_IN.value
    assert data["check_in_time"] is not None
    assert data["check_out_time"] is None


def test_get_check_in(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="get_checkin@example.com",
    )

    create_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    check_in_id = create_response.json()["id"]

    response = client.get(
        f"/check-ins/{check_in_id}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == check_in_id


def test_get_check_ins_by_attendee(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="attendee_list@example.com",
    )

    client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    response = client.get(
        f"/check-ins/attendee/{attendee['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["attendee_id"] == attendee["id"]


def test_get_check_ins_by_event(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="event_list@example.com",
    )

    client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    response = client.get(
        f"/check-ins/event/{event['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["event_id"] == event["id"]


def test_duplicate_check_in_rejected(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="duplicate_checkin@example.com",
    )

    payload = {
        "attendee_id": attendee["id"],
        "event_id": event["id"],
    }

    first_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json=payload,
    )

    assert second_response.status_code == 409


def test_check_in_wrong_event_rejected(client):
    organizer_token = create_organizer(client)

    event_one = create_event(client, organizer_token)

    event_two_response = client.post(
        "/events",
        headers=auth_headers(organizer_token),
        json={
            "event_name": "Second Check-In Event",
            "description": "Second Event",
            "event_type": "Workshop",
            "start_date": (
                datetime.utcnow() + timedelta(days=3)
            ).isoformat(),
            "end_date": (
                datetime.utcnow() + timedelta(days=4)
            ).isoformat(),
            "registration_start": (
                datetime.utcnow() - timedelta(days=1)
            ).isoformat(),
            "registration_end": (
                datetime.utcnow() + timedelta(days=2)
            ).isoformat(),
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert event_two_response.status_code == 201

    event_two = event_two_response.json()

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event_one["id"],
        email="wrong_event@example.com",
    )

    response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event_two["id"],
        },
    )

    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_check_in_missing_attendee(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    response = client.post(
        "/check-ins",
        headers=auth_headers(organizer_token),
        json={
            "attendee_id": 999999,
            "event_id": event["id"],
        },
    )

    assert response.status_code == 404


def test_check_in_missing_event(client):
    organizer_token = create_organizer(client)

    response = client.post(
        "/check-ins",
        headers=auth_headers(organizer_token),
        json={
            "attendee_id": 999999,
            "event_id": 999999,
        },
    )

    assert response.status_code == 404


def test_check_out(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="checkout@example.com",
    )

    create_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    check_in_id = create_response.json()["id"]

    response = client.put(
        f"/check-ins/{check_in_id}/checkout",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == CheckInStatus.CHECKED_OUT.value
    assert data["check_out_time"] is not None


def test_duplicate_check_out_rejected(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="duplicate_checkout@example.com",
    )

    create_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    check_in_id = create_response.json()["id"]

    first_response = client.put(
        f"/check-ins/{check_in_id}/checkout",
        headers=auth_headers(attendee_token),
    )

    assert first_response.status_code == 200

    second_response = client.put(
        f"/check-ins/{check_in_id}/checkout",
        headers=auth_headers(attendee_token),
    )

    assert second_response.status_code == 400


def test_reactivate_checked_out_attendee(client):
    organizer_token = create_organizer(client)
    event = create_event(client, organizer_token)

    attendee, attendee_token = create_attendee(
        client,
        organizer_token,
        event["id"],
        email="reactivate@example.com",
    )

    create_response = client.post(
        "/check-ins",
        headers=auth_headers(attendee_token),
        json={
            "attendee_id": attendee["id"],
            "event_id": event["id"],
        },
    )

    check_in_id = create_response.json()["id"]

    checkout_response = client.put(
        f"/check-ins/{check_in_id}/checkout",
        headers=auth_headers(attendee_token),
    )

    assert checkout_response.status_code == 200

    response = client.put(
        f"/check-ins/{check_in_id}",
        headers=auth_headers(attendee_token),
        json={
            "status": CheckInStatus.CHECKED_IN.value,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == CheckInStatus.CHECKED_IN.value
    assert response.json()["check_out_time"] is None