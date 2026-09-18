import pytest

from app.models.notification import NotificationStatus


def register_user(client, email, role="Attendee"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": email.split("@")[0],
            "email": email,
            "password": "Password@123",
            "role": role,
        },
    )

    assert response.status_code in (200, 201), response.text

    return response.json()


def login_user(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Password@123",
        },
    )

    assert response.status_code == 200, response.text

    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture()
def notification_users(client):
    user1 = register_user(
        client,
        "notification_user1@example.com",
    )

    user2 = register_user(
        client,
        "notification_user2@example.com",
    )

    token1 = login_user(
        client,
        "notification_user1@example.com",
    )

    token2 = login_user(
        client,
        "notification_user2@example.com",
    )

    return {
        "user1": user1,
        "user2": user2,
        "token1": token1,
        "token2": token2,
    }


def create_notification(
    client,
    user_id,
    token,
    title="Test Notification",
    notification_type="General",
):
    response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "user_id": user_id,
            "title": title,
            "message": "This is a test notification.",
            "notification_type": notification_type,
        },
    )

    return response


def test_create_notification(client, notification_users):
    users = notification_users

    response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == users["user1"]["id"]
    assert data["title"] == "Test Notification"
    assert data["message"] == "This is a test notification."
    assert data["notification_type"] == "General"
    assert data["status"] == "Unread"
    assert data["read_at"] is None


def test_list_current_user_notifications(client, notification_users):
    users = notification_users

    create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
        title="User 1 Notification",
    )

    create_notification(
        client,
        users["user2"]["id"],
        users["token2"],
        title="User 2 Notification",
    )

    response = client.get(
        "/notifications",
        headers=auth_headers(users["token1"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == users["user1"]["id"]
    assert data[0]["title"] == "User 1 Notification"


def test_filter_notifications_by_status(client, notification_users):
    users = notification_users

    create_response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    notification_id = create_response.json()["id"]

    unread_response = client.get(
        "/notifications?status=Unread",
        headers=auth_headers(users["token1"]),
    )

    assert unread_response.status_code == 200
    assert len(unread_response.json()) == 1
    assert unread_response.json()[0]["id"] == notification_id

    read_response = client.get(
        "/notifications?status=Read",
        headers=auth_headers(users["token1"]),
    )

    assert read_response.status_code == 200
    assert len(read_response.json()) == 0


def test_mark_notification_as_read(client, notification_users):
    users = notification_users

    create_response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    notification_id = create_response.json()["id"]

    response = client.put(
        f"/notifications/{notification_id}/read",
        headers=auth_headers(users["token1"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notification_id
    assert data["status"] == "Read"
    assert data["read_at"] is not None


def test_notification_read_ownership_check(client, notification_users):
    users = notification_users

    create_response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    notification_id = create_response.json()["id"]

    response = client.put(
        f"/notifications/{notification_id}/read",
        headers=auth_headers(users["token2"]),
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_delete_notification(client, notification_users):
    users = notification_users

    create_response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    notification_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/notifications/{notification_id}",
        headers=auth_headers(users["token1"]),
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        "/notifications",
        headers=auth_headers(users["token1"]),
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 0


def test_notification_delete_ownership_check(client, notification_users):
    users = notification_users

    create_response = create_notification(
        client,
        users["user1"]["id"],
        users["token1"],
    )

    notification_id = create_response.json()["id"]

    response = client.delete(
        f"/notifications/{notification_id}",
        headers=auth_headers(users["token2"]),
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_notification_not_found_for_read(client, notification_users):
    users = notification_users

    response = client.put(
        "/notifications/999999/read",
        headers=auth_headers(users["token1"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_notification_not_found_for_delete(client, notification_users):
    users = notification_users

    response = client.delete(
        "/notifications/999999",
        headers=auth_headers(users["token1"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_create_notification_requires_authentication(client, notification_users):
    users = notification_users

    response = client.post(
        "/notifications",
        json={
            "user_id": users["user1"]["id"],
            "title": "Unauthorized Notification",
            "message": "This should not be created.",
            "notification_type": "General",
        },
    )

    assert response.status_code in (401, 403)


def test_list_notifications_requires_authentication(client):
    response = client.get("/notifications")

    assert response.status_code in (401, 403)

def test_attendee_registration_creates_notification(client):
    organizer = register_user(
        client,
        "auto_notification_organizer@example.com",
        "Event Organizer",
    )

    organizer_token = login_user(
        client,
        "auto_notification_organizer@example.com",
    )

    event_response = client.post(
        "/events",
        headers=auth_headers(organizer_token),
        json={
            "event_name": "Automatic Notification Event",
            "description": "Testing automatic registration notification",
            "event_type": "Conference",
            "organizer_id": organizer["id"],
            "start_date": "2026-11-10T09:00:00",
            "end_date": "2026-11-10T18:00:00",
            "registration_start": "2026-10-01T09:00:00",
            "registration_end": "2026-11-09T18:00:00",
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert event_response.status_code == 201

    event_id = event_response.json()["id"]

    attendee = register_user(
        client,
        "auto_notification_attendee@example.com",
    )

    attendee_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert attendee_response.status_code == 201

    attendee_token = login_user(
        client,
        "auto_notification_attendee@example.com",
    )

    notification_response = client.get(
        "/notifications",
        headers=auth_headers(attendee_token),
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()

    assert len(notifications) == 1

    notification = notifications[0]

    assert notification["user_id"] == attendee["id"]
    assert notification["title"] == "Event Registration Successful"
    assert notification["notification_type"] == "Registration"
    assert notification["status"] == "Unread"
    assert event_response.json()["event_name"] in notification["message"]

def test_ticket_purchase_creates_notification(client):
    organizer = register_user(
        client,
        "ticket_notification_organizer@example.com",
        "Event Organizer",
    )

    organizer_token = login_user(
        client,
        "ticket_notification_organizer@example.com",
    )

    event_response = client.post(
        "/events",
        headers=auth_headers(organizer_token),
        json={
            "event_name": "Ticket Notification Event",
            "description": "Testing ticket purchase notification",
            "event_type": "Conference",
            "organizer_id": organizer["id"],
            "start_date": "2026-12-10T09:00:00",
            "end_date": "2026-12-10T18:00:00",
            "registration_start": "2026-11-01T09:00:00",
            "registration_end": "2026-12-09T18:00:00",
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    attendee = register_user(
        client,
        "ticket_notification_attendee@example.com",
    )

    attendee_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert attendee_response.status_code == 201
    attendee_id = attendee_response.json()["id"]

    ticket_response = client.post(
        "/tickets",
        headers=auth_headers(organizer_token),
        json={
            "event_id": event_id,
            "ticket_name": "Regular Ticket",
            "ticket_type": "Regular",
            "price": 1000,
            "quantity": 50,
            "available_quantity": 50,
            "status": "Available",
        },
    )

    assert ticket_response.status_code == 201
    ticket_id = ticket_response.json()["id"]

    purchase_response = client.post(
        "/ticket-purchases",
        headers=auth_headers(organizer_token),
        json={
            "ticket_id": ticket_id,
            "attendee_id": attendee_id,
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201

    attendee_token = login_user(
        client,
        "ticket_notification_attendee@example.com",
    )

    notification_response = client.get(
        "/notifications",
        headers=auth_headers(attendee_token),
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()

    ticket_notifications = [
        notification
        for notification in notifications
        if notification["notification_type"] == "Ticket Purchase"
    ]

    assert len(ticket_notifications) == 1

    notification = ticket_notifications[0]

    assert notification["user_id"] == attendee["id"]
    assert notification["title"] == "Ticket Purchase Successful"
    assert notification["status"] == "Unread"
    assert "Ticket Notification Event" in notification["message"]
    assert "2 ticket(s)" in notification["message"]
    assert "2000.00" in notification["message"]

def test_payment_success_creates_notification(client):
    organizer = register_user(
        client,
        "payment_success_organizer@example.com",
        "Event Organizer",
    )

    organizer_token = login_user(
        client,
        "payment_success_organizer@example.com",
    )

    event_response = client.post(
        "/events",
        headers=auth_headers(organizer_token),
        json={
            "event_name": "Payment Success Event",
            "description": "Testing payment success notification",
            "event_type": "Conference",
            "organizer_id": organizer["id"],
            "start_date": "2027-01-10T09:00:00",
            "end_date": "2027-01-10T18:00:00",
            "registration_start": "2026-12-01T09:00:00",
            "registration_end": "2027-01-09T18:00:00",
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    attendee = register_user(
        client,
        "payment_success_attendee@example.com",
    )

    attendee_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert attendee_response.status_code == 201
    attendee_id = attendee_response.json()["id"]

    ticket_response = client.post(
        "/tickets",
        headers=auth_headers(organizer_token),
        json={
            "event_id": event_id,
            "ticket_name": "Payment Success Ticket",
            "ticket_type": "Regular",
            "price": 500,
            "quantity": 20,
            "available_quantity": 20,
            "status": "Available",
        },
    )

    assert ticket_response.status_code == 201
    ticket_id = ticket_response.json()["id"]

    purchase_response = client.post(
        "/ticket-purchases",
        headers=auth_headers(organizer_token),
        json={
            "ticket_id": ticket_id,
            "attendee_id": attendee_id,
            "quantity": 2,
        },
    )

    assert purchase_response.status_code == 201
    purchase_id = purchase_response.json()["id"]

    payment_response = client.put(
        f"/ticket-purchases/{purchase_id}/payment",
        headers=auth_headers(organizer_token),
        json={
            "payment_status": "Success",
        },
    )

    assert payment_response.status_code == 200

    payment_data = payment_response.json()

    assert payment_data["payment_status"] == "Success"
    assert payment_data["payment_reference"] == (
        f"PAY-{purchase_id:06d}"
    )

    attendee_token = login_user(
        client,
        "payment_success_attendee@example.com",
    )

    notification_response = client.get(
        "/notifications",
        headers=auth_headers(attendee_token),
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()

    payment_notifications = [
        notification
        for notification in notifications
        if notification["notification_type"] == "Payment"
    ]

    assert len(payment_notifications) == 1

    notification = payment_notifications[0]

    assert notification["user_id"] == attendee["id"]
    assert notification["title"] == "Payment Successful"
    assert notification["status"] == "Unread"
    assert "1000.00" in notification["message"]


def test_payment_failed_creates_notification(client):
    organizer = register_user(
        client,
        "payment_failed_organizer@example.com",
        "Event Organizer",
    )

    organizer_token = login_user(
        client,
        "payment_failed_organizer@example.com",
    )

    event_response = client.post(
        "/events",
        headers=auth_headers(organizer_token),
        json={
            "event_name": "Payment Failed Event",
            "description": "Testing payment failure notification",
            "event_type": "Conference",
            "organizer_id": organizer["id"],
            "start_date": "2027-02-10T09:00:00",
            "end_date": "2027-02-10T18:00:00",
            "registration_start": "2027-01-01T09:00:00",
            "registration_end": "2027-02-09T18:00:00",
            "capacity": 100,
            "status": "Registration Open",
        },
    )

    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    attendee = register_user(
        client,
        "payment_failed_attendee@example.com",
    )

    attendee_response = client.post(
        "/attendees",
        headers=auth_headers(organizer_token),
        json={
            "user_id": attendee["id"],
            "event_id": event_id,
        },
    )

    assert attendee_response.status_code == 201
    attendee_id = attendee_response.json()["id"]

    ticket_response = client.post(
        "/tickets",
        headers=auth_headers(organizer_token),
        json={
            "event_id": event_id,
            "ticket_name": "Payment Failed Ticket",
            "ticket_type": "Regular",
            "price": 750,
            "quantity": 20,
            "available_quantity": 20,
            "status": "Available",
        },
    )

    assert ticket_response.status_code == 201
    ticket_id = ticket_response.json()["id"]

    purchase_response = client.post(
        "/ticket-purchases",
        headers=auth_headers(organizer_token),
        json={
            "ticket_id": ticket_id,
            "attendee_id": attendee_id,
            "quantity": 1,
        },
    )

    assert purchase_response.status_code == 201
    purchase_id = purchase_response.json()["id"]

    payment_response = client.put(
        f"/ticket-purchases/{purchase_id}/payment",
        headers=auth_headers(organizer_token),
        json={
            "payment_status": "Failed",
        },
    )

    assert payment_response.status_code == 200

    payment_data = payment_response.json()

    assert payment_data["payment_status"] == "Failed"
    assert payment_data["purchase_status"] == "Cancelled"

    attendee_token = login_user(
        client,
        "payment_failed_attendee@example.com",
    )

    notification_response = client.get(
        "/notifications",
        headers=auth_headers(attendee_token),
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()

    payment_notifications = [
        notification
        for notification in notifications
        if notification["notification_type"] == "Payment"
    ]

    assert len(payment_notifications) == 1

    notification = payment_notifications[0]

    assert notification["user_id"] == attendee["id"]
    assert notification["title"] == "Payment Failed"
    assert notification["status"] == "Unread"
    assert "750.00" in notification["message"]