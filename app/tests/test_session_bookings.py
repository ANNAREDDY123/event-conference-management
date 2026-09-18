from datetime import datetime, timedelta

from app.models.attendee import Attendee
from app.models.event import Event, EventStatus, EventType
from app.models.session import EventSession, SessionStatus, SessionType
from app.models.user import User, UserRole
from app.models.venue import (
    Hall,
    HallAvailabilityStatus,
    Venue,
    VenueStatus,
)
from app.utils.security import hash_password


def create_user(
    db,
    email="attendee@test.com",
    role=UserRole.ATTENDEE,
    full_name="Test User",
):
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password("Test@123"),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_event(db, organizer_id, name="Test Event"):
    now = datetime.utcnow()

    event = Event(
        event_name=name,
        description="Test event",
        event_type=EventType.CONFERENCE,
        organizer_id=organizer_id,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        registration_start=now - timedelta(days=1),
        registration_end=now + timedelta(days=1),
        capacity=100,
        status=EventStatus.REGISTRATION_OPEN,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def create_venue_and_hall(db):
    venue = Venue(
        venue_name="Test Venue",
        address="Test Address",
        city="Hyderabad",
        capacity=100,
        facilities="Projector, WiFi",
        status=VenueStatus.ACTIVE,
    )

    db.add(venue)
    db.commit()
    db.refresh(venue)

    hall = Hall(
        venue_id=venue.id,
        hall_name="Main Hall",
        capacity=50,
        floor=1,
        availability_status=HallAvailabilityStatus.AVAILABLE,
    )

    db.add(hall)
    db.commit()
    db.refresh(hall)

    return venue, hall


def create_session(db, event_id, hall_id, capacity=2):
    event = db.get(Event, event_id)

    session = EventSession(
        event_id=event_id,
        speaker_id=None,
        hall_id=hall_id,
        title="Python Session",
        description="FastAPI and Python",
        session_type=SessionType.TECHNICAL,
        start_time=event.start_date + timedelta(hours=1),
        end_time=event.start_date + timedelta(hours=2),
        capacity=capacity,
        status=SessionStatus.SCHEDULED,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def create_attendee(db, user_id, event_id):
    attendee = Attendee(
        user_id=user_id,
        event_id=event_id,
        status="Registered",
    )

    db.add(attendee)
    db.commit()
    db.refresh(attendee)

    return attendee


def register_and_login(client, email, full_name="API Test User"):
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": "Test@123",
            "role": "Attendee",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def setup_booking_data(db):
    organizer = create_user(
        db,
        email="organizer@test.com",
        role=UserRole.EVENT_ORGANIZER,
        full_name="Test Organizer",
    )

    attendee_user = create_user(
        db,
        email="attendee@test.com",
        role=UserRole.ATTENDEE,
        full_name="Test Attendee",
    )

    event = create_event(
        db,
        organizer.id,
    )

    _, hall = create_venue_and_hall(db)

    session = create_session(
        db,
        event.id,
        hall.id,
        capacity=2,
    )

    attendee = create_attendee(
        db,
        attendee_user.id,
        event.id,
    )

    return attendee, session


def test_create_session_booking(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "api_user@test.com",
    )

    response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["attendee_id"] == attendee.id
    assert data["session_id"] == session.id
    assert data["status"] == "Booked"


def test_duplicate_session_booking_is_rejected(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "duplicate@test.com",
    )

    first = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert first.status_code == 201

    second = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert second.status_code == 409
    assert "already booked" in second.json()["detail"]


def test_session_capacity_is_enforced(client, db):
    attendee1, session = setup_booking_data(db)

    user2 = create_user(
        db,
        email="attendee2@test.com",
        role=UserRole.ATTENDEE,
        full_name="Second Attendee",
    )

    attendee2 = create_attendee(
        db,
        user2.id,
        session.event_id,
    )

    user3 = create_user(
        db,
        email="attendee3@test.com",
        role=UserRole.ATTENDEE,
        full_name="Third Attendee",
    )

    attendee3 = create_attendee(
        db,
        user3.id,
        session.event_id,
    )

    headers = register_and_login(
        client,
        "capacity@test.com",
    )

    first = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee1.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert first.status_code == 201

    second = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee2.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert second.status_code == 201

    third = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee3.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert third.status_code == 409
    assert "capacity" in third.json()["detail"].lower()


def test_attendee_event_mismatch_is_rejected(client, db):
    _, session = setup_booking_data(db)

    organizer2 = create_user(
        db,
        email="organizer2@test.com",
        role=UserRole.EVENT_ORGANIZER,
        full_name="Second Organizer",
    )

    event2 = create_event(
        db,
        organizer2.id,
        name="Second Event",
    )

    attendee2_user = create_user(
        db,
        email="attendee4@test.com",
        role=UserRole.ATTENDEE,
        full_name="Fourth Attendee",
    )

    attendee2 = create_attendee(
        db,
        attendee2_user.id,
        event2.id,
    )

    headers = register_and_login(
        client,
        "mismatch@test.com",
    )

    response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee2.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"]


def test_cancel_session_booking(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "cancel@test.com",
    )

    create_response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    booking_id = create_response.json()["id"]

    response = client.put(
        f"/session-bookings/{booking_id}/cancel",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"


def test_cancelled_booking_can_be_reactivated(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "reactivate@test.com",
    )

    create_response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    booking_id = create_response.json()["id"]

    cancel_response = client.put(
        f"/session-bookings/{booking_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "Cancelled"

    reactivate_response = client.put(
        f"/session-bookings/{booking_id}",
        json={
            "status": "Booked",
        },
        headers=headers,
    )

    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["status"] == "Booked"


def test_cancelled_session_cannot_be_booked(client, db):
    attendee, session = setup_booking_data(db)

    session.status = SessionStatus.CANCELLED
    db.commit()

    headers = register_and_login(
        client,
        "cancelledsession@test.com",
    )

    response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "cancelled session" in response.json()["detail"]


def test_completed_session_cannot_be_booked(client, db):
    attendee, session = setup_booking_data(db)

    session.status = SessionStatus.COMPLETED
    db.commit()

    headers = register_and_login(
        client,
        "completedsession@test.com",
    )

    response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "completed session" in response.json()["detail"]


def test_get_booking_by_attendee(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "getattendee@test.com",
    )

    create_response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/session-bookings/attendee/{attendee.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["attendee_id"] == attendee.id


def test_get_booking_by_session(client, db):
    attendee, session = setup_booking_data(db)

    headers = register_and_login(
        client,
        "getsession@test.com",
    )

    create_response = client.post(
        "/session-bookings",
        json={
            "attendee_id": attendee.id,
            "session_id": session.id,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/session-bookings/session/{session.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["session_id"] == session.id


def test_get_nonexistent_booking_returns_404(client, db):
    headers = register_and_login(
        client,
        "notfound@test.com",
    )

    response = client.get(
        "/session-bookings/99999",
        headers=headers,
    )

    assert response.status_code == 404