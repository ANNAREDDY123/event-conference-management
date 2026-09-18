from datetime import datetime, timedelta

from app.models.event import EventStatus


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_user(
    client,
    email,
    role="Attendee",
    full_name="Certificate User",
):
    response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": "Test@123",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def login(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_organizer(client, email):
    create_user(
        client,
        email=email,
        role="Event Organizer",
        full_name="Certificate Organizer",
    )
    return login(client, email)


def create_event(client, token, name="Certificate Event"):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": name,
            "description": "Certificate Test Event",
            "event_type": "Conference",
            "start_date": (
                now + timedelta(days=1)
            ).isoformat(),
            "end_date": (
                now + timedelta(days=2)
            ).isoformat(),
            "registration_start": (
                now - timedelta(days=1)
            ).isoformat(),
            "registration_end": (
                now + timedelta(hours=12)
            ).isoformat(),
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_attendee(
    client,
    event_id,
    email,
):
    user = create_user(
        client,
        email=email,
        role="Attendee",
        full_name="Certificate Attendee",
    )

    token = login(client, email)

    response = client.post(
        "/attendees",
        headers=auth_headers(token),
        json={
            "user_id": user["id"],
            "event_id": event_id,
        },
    )

    assert response.status_code == 201

    return response.json(), token


def complete_event(client, token, event_id):
    response = client.put(
        f"/events/{event_id}",
        headers=auth_headers(token),
        json={
            "status": EventStatus.COMPLETED.value,
        },
    )

    assert response.status_code == 200
    return response.json()


def create_certificate(
    client,
    token,
    attendee_id,
    event_id,
):
    response = client.post(
        "/certificates",
        headers=auth_headers(token),
        json={
            "attendee_id": attendee_id,
            "event_id": event_id,
            "certificate_type": "Participation",
        },
    )

    return response


def test_create_certificate(client):
    organizer_token = create_organizer(
        client,
        "certificate_create_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate Creation Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_create_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert response.status_code == 201

    data = response.json()

    assert data["attendee_id"] == attendee["id"]
    assert data["event_id"] == event["id"]
    assert data["certificate_number"].startswith(
        f"CERT-E{event['id']}-"
    )
    assert data["certificate_type"] == "Participation"
    assert data["issue_date"] is not None


def test_duplicate_certificate_rejected(client):
    organizer_token = create_organizer(
        client,
        "certificate_duplicate_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate Duplicate Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_duplicate_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    first_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert first_response.status_code == 201

    second_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


def test_get_certificates_by_attendee(client):
    organizer_token = create_organizer(
        client,
        "certificate_attendee_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate Attendee Lookup Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_attendee_lookup@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    certificate_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert certificate_response.status_code == 201

    response = client.get(
        f"/certificates/attendee/{attendee['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["attendee_id"] == attendee["id"]
    assert data[0]["event_id"] == event["id"]


def test_get_certificates_by_event(client):
    organizer_token = create_organizer(
        client,
        "certificate_event_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate Event Lookup Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_event_lookup@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    certificate_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert certificate_response.status_code == 201

    response = client.get(
        f"/certificates/event/{event['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["event_id"] == event["id"]


def test_get_certificate_by_id(client):
    organizer_token = create_organizer(
        client,
        "certificate_id_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate ID Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_id_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    create_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert create_response.status_code == 201

    certificate_id = create_response.json()["id"]

    response = client.get(
        f"/certificates/{certificate_id}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == certificate_id


def test_delete_certificate(client):
    organizer_token = create_organizer(
        client,
        "certificate_delete_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Certificate Delete Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "certificate_delete_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    create_response = create_certificate(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert create_response.status_code == 201

    certificate_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/certificates/{certificate_id}",
        headers=auth_headers(attendee_token),
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/certificates/{certificate_id}",
        headers=auth_headers(attendee_token),
    )

    assert get_response.status_code == 404