from datetime import datetime, timedelta

from app.models.attendee import Attendee
from app.models.event import EventStatus
from app.models.notification import Notification, NotificationType
from app.models.ticket_purchase import PaymentStatus, PurchaseStatus


# ============================================================
# TEST HELPERS
# ============================================================

def create_user(
    client,
    email,
    role,
    full_name="Level 16 Test User",
):
    response = client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": "TestPassword123",
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
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_organizer(client, suffix):
    user = create_user(
        client,
        f"level16.organizer.{suffix}@example.com",
        "Event Organizer",
        "Level 16 Organizer",
    )

    token = login(
        client,
        user["email"],
    )

    return user, token


def create_attendee(client, suffix):
    user = create_user(
        client,
        f"level16.attendee.{suffix}@example.com",
        "Attendee",
        "Level 16 Attendee",
    )

    token = login(
        client,
        user["email"],
    )

    return user, token


def create_event(
    client,
    organizer_token,
    organizer_id,
    suffix,
):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        json={
            "event_name": f"Level 16 Event {suffix}",
            "description": "Cancellation and refund test event",
            "event_type": "Conference",
            "organizer_id": organizer_id,
            "start_date": (
                now + timedelta(days=30)
            ).isoformat(),
            "end_date": (
                now + timedelta(days=30, hours=8)
            ).isoformat(),
            "registration_start": (
                now + timedelta(days=1)
            ).isoformat(),
            "registration_end": (
                now + timedelta(days=29)
            ).isoformat(),
            "capacity": 100,
            "status": "Registration Open",
        },
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 201
    return response.json()


def create_attendee_registration(
    client,
    attendee_token,
    attendee_user_id,
    event_id,
):
    response = client.post(
        "/attendees",
        json={
            "user_id": attendee_user_id,
            "event_id": event_id,
        },
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 201
    return response.json()


def create_ticket(
    client,
    organizer_token,
    event_id,
    quantity=10,
):
    response = client.post(
        "/tickets",
        json={
            "event_id": event_id,
            "ticket_name": "Level 16 Regular Ticket",
            "ticket_type": "Regular",
            "price": 1000,
            "quantity": quantity,
            "status": "Available",
        },
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 201
    return response.json()


def purchase_ticket(
    client,
    attendee_token,
    ticket_id,
    attendee_id,
    quantity=1,
):
    response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket_id,
            "attendee_id": attendee_id,
            "quantity": quantity,
        },
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 201
    return response.json()


def mark_payment_success(
    client,
    attendee_token,
    purchase_id,
):
    response = client.put(
        f"/ticket-purchases/{purchase_id}/payment",
        json={
            "payment_status": "Success",
        },
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200
    return response.json()


def cancel_event(
    client,
    organizer_token,
    event_id,
):
    response = client.put(
        f"/events/{event_id}",
        json={
            "status": "Cancelled",
        },
        headers=auth_headers(organizer_token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"

    return response.json()


# ============================================================
# SUCCESSFUL REFUND
# ============================================================

def test_event_cancellation_refunds_successful_purchase(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "successful-refund",
    )

    attendee, attendee_token = create_attendee(
        client,
        "successful-refund",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "successful-refund",
    )

    attendee_registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        attendee_registration["id"],
        quantity=2,
    )

    payment = mark_payment_success(
        client,
        attendee_token,
        purchase["id"],
    )

    assert payment["payment_status"] == "Success"

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    purchase_response = client.get(
        f"/ticket-purchases/{purchase['id']}",
        headers=auth_headers(attendee_token),
    )

    assert purchase_response.status_code == 200

    data = purchase_response.json()

    assert data["payment_status"] == "Refunded"
    assert data["purchase_status"] == "Cancelled"


# ============================================================
# TICKET QUANTITY RESTORATION
# ============================================================

def test_event_cancellation_restores_ticket_quantity(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "quantity-restoration",
    )

    attendee, attendee_token = create_attendee(
        client,
        "quantity-restoration",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "quantity-restoration",
    )

    registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        registration["id"],
        quantity=3,
    )

    mark_payment_success(
        client,
        attendee_token,
        purchase["id"],
    )

    ticket_after_purchase = client.get(
        f"/tickets/{ticket['id']}",
        headers=auth_headers(organizer_token),
    )

    assert ticket_after_purchase.status_code == 200

    available_before_cancel = (
        ticket_after_purchase.json()["available_quantity"]
    )

    assert available_before_cancel == 7

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    ticket_after_refund = client.get(
        f"/tickets/{ticket['id']}",
        headers=auth_headers(organizer_token),
    )

    assert ticket_after_refund.status_code == 200

    available_after_cancel = (
        ticket_after_refund.json()["available_quantity"]
    )

    assert available_after_cancel == 10
    assert ticket_after_refund.json()["status"] == "Available"


# ============================================================
# EVENT CANCELLATION NOTIFICATION
# ============================================================

def test_event_cancellation_creates_attendee_notification(
    client,
    db,
):
    organizer, organizer_token = create_organizer(
        client,
        "event-notification",
    )

    attendee, attendee_token = create_attendee(
        client,
        "event-notification",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "event-notification",
    )

    create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == attendee["id"],
            Notification.notification_type
            == NotificationType.EVENT_CANCELLATION,
        )
        .all()
    )

    assert len(notifications) >= 1

    notification = notifications[-1]

    assert notification.title == "Event Cancelled"
    assert event["event_name"] in notification.message


# ============================================================
# REFUND NOTIFICATION
# ============================================================

def test_event_cancellation_creates_refund_notification(
    client,
    db,
):
    organizer, organizer_token = create_organizer(
        client,
        "refund-notification",
    )

    attendee, attendee_token = create_attendee(
        client,
        "refund-notification",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "refund-notification",
    )

    registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        registration["id"],
        quantity=2,
    )

    mark_payment_success(
        client,
        attendee_token,
        purchase["id"],
    )

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == attendee["id"],
            Notification.notification_type
            == NotificationType.REFUND,
        )
        .all()
    )

    assert len(notifications) >= 1

    notification = notifications[-1]

    assert notification.title == "Ticket Purchase Refunded"
    assert "refunded successfully" in notification.message
    assert "2000.00" in notification.message


# ============================================================
# PENDING PAYMENT
# ============================================================

def test_event_cancellation_does_not_refund_pending_payment(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "pending-payment",
    )

    attendee, attendee_token = create_attendee(
        client,
        "pending-payment",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "pending-payment",
    )

    registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        registration["id"],
        quantity=2,
    )

    assert purchase["payment_status"] == "Pending"

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    response = client.get(
        f"/ticket-purchases/{purchase['id']}",
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_status"] == "Pending"
    assert data["purchase_status"] == "Confirmed"


# ============================================================
# FAILED PAYMENT
# ============================================================

def test_event_cancellation_does_not_refund_failed_payment(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "failed-payment",
    )

    attendee, attendee_token = create_attendee(
        client,
        "failed-payment",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "failed-payment",
    )

    registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        registration["id"],
        quantity=2,
    )

    response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Failed",
        },
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 200

    assert response.json()["payment_status"] == "Failed"
    assert response.json()["purchase_status"] == "Cancelled"

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    purchase_response = client.get(
        f"/ticket-purchases/{purchase['id']}",
        headers=auth_headers(attendee_token),
    )

    assert purchase_response.status_code == 200

    data = purchase_response.json()

    assert data["payment_status"] == "Failed"
    assert data["purchase_status"] == "Cancelled"


# ============================================================
# DUPLICATE REFUND PROTECTION
# ============================================================

def test_event_cancellation_does_not_duplicate_refund(
    client,
    db,
):
    organizer, organizer_token = create_organizer(
        client,
        "duplicate-refund",
    )

    attendee, attendee_token = create_attendee(
        client,
        "duplicate-refund",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "duplicate-refund",
    )

    registration = create_attendee_registration(
        client,
        attendee_token,
        attendee["id"],
        event["id"],
    )

    ticket = create_ticket(
        client,
        organizer_token,
        event["id"],
        quantity=10,
    )

    purchase = purchase_ticket(
        client,
        attendee_token,
        ticket["id"],
        registration["id"],
        quantity=2,
    )

    mark_payment_success(
        client,
        attendee_token,
        purchase["id"],
    )

    cancel_event(
        client,
        organizer_token,
        event["id"],
    )

    refund_count_before = (
        db.query(Notification)
        .filter(
            Notification.user_id == attendee["id"],
            Notification.notification_type
            == NotificationType.REFUND,
        )
        .count()
    )

    # Calling cancellation again must not create
    # another refund.
    second_cancel = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=auth_headers(organizer_token),
    )

    assert second_cancel.status_code == 200

    refund_count_after = (
        db.query(Notification)
        .filter(
            Notification.user_id == attendee["id"],
            Notification.notification_type
            == NotificationType.REFUND,
        )
        .count()
    )

    assert refund_count_after == refund_count_before


# ============================================================
# UNAUTHORIZED ORGANIZER
# ============================================================

def test_other_organizer_cannot_cancel_event(
    client,
):
    organizer1, organizer1_token = create_organizer(
        client,
        "owner",
    )

    organizer2, organizer2_token = create_organizer(
        client,
        "other",
    )

    event = create_event(
        client,
        organizer1_token,
        organizer1["id"],
        "unauthorized",
    )

    response = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=auth_headers(organizer2_token),
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to update this event"
    )


# ============================================================
# ATTENDEE CANNOT CANCEL EVENT
# ============================================================

def test_attendee_cannot_cancel_event(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "attendee-cancel",
    )

    attendee, attendee_token = create_attendee(
        client,
        "attendee-cancel",
    )

    event = create_event(
        client,
        organizer_token,
        organizer["id"],
        "attendee-cancel",
    )

    response = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=auth_headers(attendee_token),
    )

    assert response.status_code == 403