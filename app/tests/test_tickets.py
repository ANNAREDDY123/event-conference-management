from datetime import datetime, timedelta

from app.models.user import UserRole


def register_user(client, email, role):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Ticket Test User",
            "email": email,
            "password": "Test@123",
            "role": role.value,
        },
    )

    assert response.status_code == 201

    user = response.json()

    # Login to get access token
    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Authenticate all subsequent requests
    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return user


def create_event(client, organizer_id, capacity=100):
    response = client.post(
        "/events",
        json={
            "event_name": "Ticket Test Event",
            "description": "Event for ticket testing",
            "event_type": "Conference",
            "organizer_id": organizer_id,
            "start_date": (
                datetime.now() + timedelta(days=10)
            ).isoformat(),
            "end_date": (
                datetime.now() + timedelta(days=11)
            ).isoformat(),
            "registration_start": (
                datetime.now() + timedelta(days=1)
            ).isoformat(),
            "registration_end": (
                datetime.now() + timedelta(days=9)
            ).isoformat(),
            "capacity": capacity,
            "status": "Registration Open",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_ticket(client, event_id, quantity=50):
    response = client.post(
        "/tickets",
        json={
            "event_id": event_id,
            "ticket_name": "Regular Ticket",
            "ticket_type": "Regular",
            "price": 999.0,
            "quantity": quantity,
            "status": "Available",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_ticket(client):
    organizer = register_user(
        client,
        "ticket_create@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])

    response = client.post(
        "/tickets",
        json={
            "event_id": event["id"],
            "ticket_name": "VIP Ticket",
            "ticket_type": "VIP",
            "price": 1999.0,
            "quantity": 25,
            "status": "Available",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_id"] == event["id"]
    assert data["ticket_name"] == "VIP Ticket"
    assert data["ticket_type"] == "VIP"
    assert data["price"] == 1999.0
    assert data["quantity"] == 25
    assert data["available_quantity"] == 25
    assert data["status"] == "Available"


def test_get_ticket(client):
    organizer = register_user(
        client,
        "ticket_get@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])
    ticket = create_ticket(client, event["id"])

    response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == ticket["id"]


def test_get_tickets(client):
    organizer = register_user(
        client,
        "ticket_list@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])

    create_ticket(
        client,
        event["id"],
    )

    response = client.get("/tickets")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_tickets_by_event(client):
    organizer = register_user(
        client,
        "ticket_event@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])

    create_ticket(
        client,
        event["id"],
    )

    response = client.get(
        f"/tickets/event/{event['id']}"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["event_id"] == event["id"]


def test_update_ticket(client):
    organizer = register_user(
        client,
        "ticket_update@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])

    ticket = create_ticket(
        client,
        event["id"],
        quantity=50,
    )

    response = client.put(
        f"/tickets/{ticket['id']}",
        json={
            "ticket_name": "Updated VIP Ticket",
            "price": 2499.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ticket_name"] == "Updated VIP Ticket"
    assert data["price"] == 2499.0
    assert data["available_quantity"] == 50


def test_update_ticket_quantity(client):
    organizer = register_user(
        client,
        "ticket_quantity@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(client, organizer["id"])

    ticket = create_ticket(
        client,
        event["id"],
        quantity=50,
    )

    response = client.put(
        f"/tickets/{ticket['id']}",
        json={
            "quantity": 75,
        },
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 75
    assert response.json()["available_quantity"] == 75


def test_create_ticket_nonexistent_event(client):
    register_user(
        client,
        "ticket_invalid_event@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    response = client.post(
        "/tickets",
        json={
            "event_id": 99999,
            "ticket_name": "Regular Ticket",
            "ticket_type": "Regular",
            "price": 999.0,
            "quantity": 10,
            "status": "Available",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_create_ticket_exceeds_event_capacity(client):
    organizer = register_user(
        client,
        "ticket_capacity@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(
        client,
        organizer["id"],
        capacity=20,
    )

    response = client.post(
        "/tickets",
        json={
            "event_id": event["id"],
            "ticket_name": "Large Ticket Batch",
            "ticket_type": "Regular",
            "price": 500.0,
            "quantity": 25,
            "status": "Available",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Total ticket quantity cannot exceed event capacity"
    )


def test_get_nonexistent_ticket(client):
    register_user(
        client,
        "ticket_not_found@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    response = client.get(
        "/tickets/99999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_delete_ticket(client):
    organizer = register_user(
        client,
        "ticket_delete@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(
        client,
        organizer["id"],
    )

    ticket = create_ticket(
        client,
        event["id"],
    )

    response = client.delete(
        f"/tickets/{ticket['id']}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert response.status_code == 404