from datetime import datetime, timedelta

from app.models.event import EventStatus


# =========================================================
# HELPERS
# =========================================================

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_user(
    client,
    email,
    role="Attendee",
    full_name="Dashboard User",
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


def create_admin(client, email):
    create_user(
        client,
        email=email,
        role="Admin",
        full_name="Dashboard Admin",
    )

    return login(client, email)


def create_organizer(client, email):
    create_user(
        client,
        email=email,
        role="Event Organizer",
        full_name="Dashboard Organizer",
    )

    return login(client, email)


def create_attendee(client, event_id, email):
    user = create_user(
        client,
        email=email,
        role="Attendee",
        full_name="Dashboard Attendee",
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


def create_event(
    client,
    token,
    name="Dashboard Test Event",
    status="Registration Open",
):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        headers=auth_headers(token),
        json={
            "event_name": name,
            "description": "Dashboard test event",
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
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def test_admin_dashboard_requires_admin_role(client):
    organizer_token = create_organizer(
        client,
        "dashboard_admin_role_organizer@example.com",
    )

    response = client.get(
        "/dashboard/admin",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 403


def test_admin_dashboard_returns_required_metrics(client):
    admin_token = create_admin(
        client,
        "dashboard_admin_metrics@example.com",
    )

    response = client.get(
        "/dashboard/admin",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    data = response.json()

    required_fields = [
        "total_events",
        "active_events",
        "completed_events",
        "total_attendees",
        "total_registrations",
        "total_tickets_sold",
        "total_revenue",
        "total_refunds",
        "average_event_rating",
    ]

    for field in required_fields:
        assert field in data


def test_admin_dashboard_counts_events(client):
    admin_token = create_admin(
        client,
        "dashboard_event_counts_admin@example.com",
    )

    organizer_token = create_organizer(
        client,
        "dashboard_event_counts_organizer@example.com",
    )

    create_event(
        client,
        organizer_token,
        "Dashboard Active Event",
        "Registration Open",
    )

    create_event(
        client,
        organizer_token,
        "Dashboard Published Event",
        "Published",
    )

    create_event(
        client,
        organizer_token,
        "Dashboard Completed Event",
        "Completed",
    )

    response = client.get(
        "/dashboard/admin",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] >= 3
    assert data["active_events"] >= 2
    assert data["completed_events"] >= 1


def test_admin_dashboard_empty_metrics_are_numeric(client):
    admin_token = create_admin(
        client,
        "dashboard_empty_admin@example.com",
    )

    response = client.get(
        "/dashboard/admin",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["total_events"], int)
    assert isinstance(data["active_events"], int)
    assert isinstance(data["completed_events"], int)
    assert isinstance(data["total_attendees"], int)
    assert isinstance(data["total_registrations"], int)
    assert isinstance(data["total_tickets_sold"], int)
    assert isinstance(data["total_revenue"], (int, float))
    assert isinstance(data["total_refunds"], (int, float))
    assert isinstance(data["average_event_rating"], (int, float))


# =========================================================
# ORGANIZER DASHBOARD
# =========================================================

def test_organizer_dashboard_requires_organizer_role(client):
    attendee = create_user(
        client,
        "dashboard_attendee_role@example.com",
        role="Attendee",
    )

    attendee_token = login(
        client,
        "dashboard_attendee_role@example.com",
    )

    response = client.get(
        "/dashboard/organizer",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403


def test_organizer_dashboard_returns_own_events(client):
    organizer_token = create_organizer(
        client,
        "dashboard_own_events@example.com",
    )

    create_event(
        client,
        organizer_token,
        "Organizer Dashboard Event",
    )

    response = client.get(
        "/dashboard/organizer",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "organizer_id" in data
    assert "total_events" in data
    assert "events" in data

    assert data["total_events"] >= 1
    assert len(data["events"]) >= 1

    event = data["events"][0]

    required_fields = [
        "event_id",
        "event_name",
        "registrations",
        "ticket_sales",
        "revenue",
        "attendance",
        "session_bookings",
    ]

    for field in required_fields:
        assert field in event


def test_organizer_dashboard_does_not_show_other_organizers_events(
    client,
):
    organizer_one = create_organizer(
        client,
        "dashboard_organizer_one@example.com",
    )

    organizer_two = create_organizer(
        client,
        "dashboard_organizer_two@example.com",
    )

    event_one = create_event(
        client,
        organizer_one,
        "Organizer One Event",
    )

    event_two = create_event(
        client,
        organizer_two,
        "Organizer Two Event",
    )

    response = client.get(
        "/dashboard/organizer",
        headers=auth_headers(organizer_one),
    )

    assert response.status_code == 200

    data = response.json()

    event_ids = [
        event["event_id"]
        for event in data["events"]
    ]

    assert event_one["id"] in event_ids
    assert event_two["id"] not in event_ids


def test_organizer_dashboard_empty_events(client):
    organizer_token = create_organizer(
        client,
        "dashboard_no_events@example.com",
    )

    response = client.get(
        "/dashboard/organizer",
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "organizer_id" in data
    assert "total_events" in data
    assert "events" in data

    assert data["total_events"] == 0
    assert data["events"] == []


# =========================================================
# SPEAKER PERFORMANCE
# =========================================================

def test_speaker_performance_requires_organizer_role(client):
    attendee_email = "dashboard_speaker_attendee@example.com"

    create_user(
        client,
        attendee_email,
        role="Attendee",
        full_name="Speaker Performance Attendee",
    )

    attendee_token = login(
        client,
        attendee_email,
    )

    response = client.get(
        "/dashboard/organizer/1/speaker-performance",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403

    response = client.get(
        "/dashboard/organizer/1/speaker-performance",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403


def test_speaker_performance_rejects_other_organizers_event(
    client,
):
    organizer_one = create_organizer(
        client,
        "dashboard_speaker_owner@example.com",
    )

    organizer_two = create_organizer(
        client,
        "dashboard_speaker_other@example.com",
    )

    event = create_event(
        client,
        organizer_one,
        "Speaker Performance Owner Event",
    )

    response = client.get(
        f"/dashboard/organizer/{event['id']}/speaker-performance",
        headers=auth_headers(organizer_two),
    )

    assert response.status_code == 403


# =========================================================
# SESSION POPULARITY
# =========================================================

def test_session_popularity_requires_organizer_role(client):
    attendee_email = "dashboard_session_attendee@example.com"

    create_user(
        client,
        attendee_email,
        role="Attendee",
        full_name="Session Popularity Attendee",
    )

    attendee_token = login(
        client,
        attendee_email,
    )

    response = client.get(
        "/dashboard/organizer/1/session-popularity",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403

    response = client.get(
        "/dashboard/organizer/1/session-popularity",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403


def test_session_popularity_rejects_other_organizers_event(
    client,
):
    organizer_one = create_organizer(
        client,
        "dashboard_session_owner@example.com",
    )

    organizer_two = create_organizer(
        client,
        "dashboard_session_other@example.com",
    )

    event = create_event(
        client,
        organizer_one,
        "Session Popularity Owner Event",
    )

    response = client.get(
        f"/dashboard/organizer/{event['id']}/session-popularity",
        headers=auth_headers(organizer_two),
    )

    assert response.status_code == 403