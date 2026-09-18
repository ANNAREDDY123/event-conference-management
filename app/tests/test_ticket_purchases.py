from datetime import datetime, timedelta

from app.models.user import UserRole


def register_user(client, email, role):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Purchase Test User",
            "email": email,
            "password": "Test@123",
            "role": role.value,
        },
    )

    assert response.status_code == 201

    user = response.json()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

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
            "event_name": "Ticket Purchase Event",
            "description": "Event for purchase testing",
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


def create_attendee(client, event_id, email):
    user = register_user(
        client,
        email,
        UserRole.ATTENDEE,
    )

    response = client.post(
        "/attendees",
        json={
            "user_id": user["id"],
            "event_id": event_id,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_ticket(client, event_id, quantity=10):
    response = client.post(
        "/tickets",
        json={
            "event_id": event_id,
            "ticket_name": "Regular Ticket",
            "ticket_type": "Regular",
            "price": 1000.0,
            "quantity": quantity,
            "status": "Available",
        },
    )

    assert response.status_code == 201

    return response.json()


def setup_purchase_data(client, email_prefix="purchase"):
    organizer = register_user(
        client,
        f"{email_prefix}_organizer@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    event = create_event(
        client,
        organizer["id"],
    )

    # Register attendee.
    attendee = create_attendee(
        client,
        event["id"],
        f"{email_prefix}_attendee@example.com",
    )

    # Login again as organizer so ticket creation is authenticated.
    login_response = client.post(
        "/auth/login",
        json={
            "email": f"{email_prefix}_organizer@example.com",
            "password": "Test@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    ticket = create_ticket(
        client,
        event["id"],
    )

    return event, attendee, ticket


def test_create_ticket_purchase(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "create_purchase",
    )

    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["ticket_id"] == ticket["id"]
    assert data["attendee_id"] == attendee["id"]
    assert data["quantity"] == 2
    assert data["total_amount"] == 2000.0
    assert data["payment_status"] == "Pending"
    assert data["purchase_status"] == "Confirmed"


def test_ticket_quantity_reduced_after_purchase(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "quantity_reduced",
    )

    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 3,
        },
    )

    assert response.status_code == 201

    ticket_response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert ticket_response.status_code == 200
    assert ticket_response.json()["available_quantity"] == 7


def test_successful_payment(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "successful_payment",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_status"] == "Success"
    assert data["payment_reference"] == "PAY-000001"


def test_failed_payment(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "failed_payment",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Failed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_status"] == "Failed"
    assert data["purchase_status"] == "Cancelled"


def test_get_purchase(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "get_purchase",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    response = client.get(
        f"/ticket-purchases/{purchase['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == purchase["id"]


def test_get_all_purchases(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "get_all_purchases",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201

    response = client.get("/ticket-purchases")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_purchases_by_attendee(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "get_attendee_purchases",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201

    response = client.get(
        f"/ticket-purchases/attendee/{attendee['id']}"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["attendee_id"] == attendee["id"]


def test_get_purchases_by_ticket(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "get_ticket_purchases",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201

    response = client.get(
        f"/ticket-purchases/ticket/{ticket['id']}"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["ticket_id"] == ticket["id"]


def test_purchase_nonexistent_ticket(client):
    register_user(
        client,
        "invalid_ticket_purchase@example.com",
        UserRole.EVENT_ORGANIZER,
    )

    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": 99999,
            "attendee_id": 99999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_purchase_nonexistent_attendee(client):
    organizer = register_user(
        client,
        "invalid_attendee_purchase@example.com",
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

    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": 99999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attendee not found"


def test_purchase_exceeds_available_quantity(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "insufficient_quantity",
    )

    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 20,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Insufficient ticket quantity available"
    )

def test_successful_refund(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "successful_refund",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert refund_response.status_code == 200

    data = refund_response.json()

    assert data["id"] == purchase["id"]
    assert data["payment_status"] == "Refunded"
    assert data["purchase_status"] == "Cancelled"


def test_refund_restores_ticket_quantity(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "refund_quantity",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 3,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    ticket_response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert ticket_response.status_code == 200
    assert ticket_response.json()["available_quantity"] == 7

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert refund_response.status_code == 200

    ticket_response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert ticket_response.status_code == 200
    assert ticket_response.json()["available_quantity"] == 10


def test_refund_recovers_sold_out_ticket(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "refund_sold_out",
    )

    # Purchase all available tickets.
    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 10,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    ticket_response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert ticket_response.status_code == 200

    ticket_data = ticket_response.json()

    assert ticket_data["available_quantity"] == 0
    assert ticket_data["status"] == "Sold Out"

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert refund_response.status_code == 200

    ticket_response = client.get(
        f"/tickets/{ticket['id']}"
    )

    assert ticket_response.status_code == 200

    ticket_data = ticket_response.json()

    assert ticket_data["available_quantity"] == 10
    assert ticket_data["status"] == "Available"


def test_refund_creates_notification(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "refund_notification",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert refund_response.status_code == 200

    # Login as the attendee because notifications are
    # returned for the currently authenticated user.
    attendee_login = client.post(
        "/auth/login",
        json={
            "email": "refund_notification_attendee@example.com",
            "password": "Test@123",
        },
    )

    assert attendee_login.status_code == 200

    attendee_token = attendee_login.json()["access_token"]

    client.headers.update(
        {
            "Authorization": f"Bearer {attendee_token}"
        }
    )

    notification_response = client.get(
        "/notifications"
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()

    refund_notifications = [
        notification
        for notification in notifications
        if notification["notification_type"] == "Refund"
    ]

    assert len(refund_notifications) >= 1

    refund_notification = refund_notifications[-1]

    assert refund_notification["user_id"] == attendee["user_id"]
    assert refund_notification["title"] == "Ticket Purchase Refunded"
    assert "refunded successfully" in refund_notification["message"]
    assert "2000.00" in refund_notification["message"]

def test_cannot_refund_pending_payment(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "refund_pending",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert refund_response.status_code == 400
    assert refund_response.json()["detail"] == (
        "Only successfully paid purchases can be refunded"
    )


def test_cannot_refund_already_refunded_purchase(client):
    event, attendee, ticket = setup_purchase_data(
        client,
        "refund_duplicate",
    )

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": attendee["id"],
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    first_refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert first_refund_response.status_code == 200
    assert first_refund_response.json()["payment_status"] == "Refunded"

    second_refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund"
    )

    assert second_refund_response.status_code == 400
    assert second_refund_response.json()["detail"] == (
        "Only successfully paid purchases can be refunded"
    )