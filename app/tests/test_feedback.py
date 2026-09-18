from datetime import datetime, timedelta

from app.models.event import EventStatus


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_user(
    client,
    email,
    role="Attendee",
    full_name="Feedback User",
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
        full_name="Feedback Organizer",
    )

    return login(client, email)


def create_event(
    client,
    token,
    name="Feedback Test Event",
):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": name,
            "description": "Feedback Test Event",
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
        full_name="Feedback Attendee",
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


def complete_event(
    client,
    token,
    event_id,
):
    response = client.put(
        f"/events/{event_id}",
        headers=auth_headers(token),
        json={
            "status": EventStatus.COMPLETED.value,
        },
    )

    assert response.status_code == 200
    return response.json()


def create_feedback(
    client,
    token,
    attendee_id,
    event_id,
    rating=5,
    comments="Excellent event",
):
    return client.post(
        "/feedback",
        headers=auth_headers(token),
        json={
            "attendee_id": attendee_id,
            "event_id": event_id,
            "rating": rating,
            "comments": comments,
        },
    )


def test_create_feedback(client):
    organizer_token = create_organizer(
        client,
        "feedback_create_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Creation Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_create_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
        rating=5,
        comments="Excellent event",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["attendee_id"] == attendee["id"]
    assert data["event_id"] == event["id"]
    assert data["rating"] == 5
    assert data["comments"] == "Excellent event"
    assert data["submitted_at"] is not None


def test_rating_validation(client):
    organizer_token = create_organizer(
        client,
        "feedback_rating_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Rating Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_rating_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    # Rating below 1
    response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
        rating=0,
        comments="Invalid rating",
    )

    assert response.status_code == 422

    # Rating above 5
    response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
        rating=6,
        comments="Invalid rating",
    )

    assert response.status_code == 422


def test_duplicate_feedback_rejected(client):
    organizer_token = create_organizer(
        client,
        "feedback_duplicate_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Duplicate Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_duplicate_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    first_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert first_response.status_code == 201

    second_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
        rating=4,
        comments="Second feedback",
    )

    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


def test_get_feedbacks_by_attendee(client):
    organizer_token = create_organizer(
        client,
        "feedback_attendee_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Attendee Lookup Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_attendee_lookup@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    feedback_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert feedback_response.status_code == 201

    response = client.get(
        f"/feedback/attendee/{attendee['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["attendee_id"] == attendee["id"]
    assert data[0]["event_id"] == event["id"]


def test_get_feedbacks_by_event(client):
    organizer_token = create_organizer(
        client,
        "feedback_event_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Event Lookup Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_event_lookup@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    feedback_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert feedback_response.status_code == 201

    response = client.get(
        f"/feedback/event/{event['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["event_id"] == event["id"]


def test_get_feedback_by_id(client):
    organizer_token = create_organizer(
        client,
        "feedback_id_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback ID Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_id_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    create_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert create_response.status_code == 201

    feedback_id = create_response.json()["id"]

    response = client.get(
        f"/feedback/{feedback_id}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == feedback_id


def test_update_feedback(client):
    organizer_token = create_organizer(
        client,
        "feedback_update_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Update Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_update_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    create_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
        rating=3,
        comments="Average event",
    )

    assert create_response.status_code == 201

    feedback_id = create_response.json()["id"]

    response = client.put(
        f"/feedback/{feedback_id}",
        headers=auth_headers(attendee_token),
        json={
            "rating": 5,
            "comments": "Excellent event after update",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == feedback_id
    assert data["rating"] == 5
    assert data["comments"] == "Excellent event after update"


def test_delete_feedback(client):
    organizer_token = create_organizer(
        client,
        "feedback_delete_organizer@example.com",
    )

    event = create_event(
        client,
        organizer_token,
        "Feedback Delete Event",
    )

    attendee, attendee_token = create_attendee(
        client,
        event["id"],
        "feedback_delete_attendee@example.com",
    )

    complete_event(
        client,
        organizer_token,
        event["id"],
    )

    create_response = create_feedback(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    assert create_response.status_code == 201

    feedback_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/feedback/{feedback_id}",
        headers=auth_headers(attendee_token),
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/feedback/{feedback_id}",
        headers=auth_headers(attendee_token),
    )

    assert get_response.status_code == 404