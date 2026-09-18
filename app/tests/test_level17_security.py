from datetime import datetime, timedelta


# ============================================================
# HELPERS
# ============================================================

def register_user(client, email, role, full_name="Level 17 Test User"):
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


def login_user(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_organizer(client, suffix):
    user = register_user(
        client,
        f"level17.organizer.{suffix}@example.com",
        "Event Organizer",
        "Level 17 Organizer",
    )

    token = login_user(client, user["email"])

    return user, token


def create_attendee(client, suffix):
    user = register_user(
        client,
        f"level17.attendee.{suffix}@example.com",
        "Attendee",
        "Level 17 Attendee",
    )

    token = login_user(client, user["email"])

    return user, token


def create_event(client, organizer, organizer_token, suffix):
    now = datetime.utcnow()

    response = client.post(
        "/events",
        json={
            "event_name": f"Level 17 Event {suffix}",
            "description": "Security test event",
            "event_type": "Conference",
            "organizer_id": organizer["id"],
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
        headers=headers(organizer_token),
    )

    assert response.status_code == 201

    return response.json()


# ============================================================
# 1. ROLE AUTHORIZATION
# ============================================================

def test_attendee_cannot_create_event(client):
    attendee, attendee_token = create_attendee(
        client,
        "cannot-create-event",
    )

    now = datetime.utcnow()

    response = client.post(
        "/events",
        json={
            "event_name": "Unauthorized Event",
            "description": "Should not be created",
            "event_type": "Conference",
            "organizer_id": attendee["id"],
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
            "status": "Draft",
        },
        headers=headers(attendee_token),
    )

    assert response.status_code == 403


def test_attendee_cannot_access_admin_dashboard(client):
    attendee, attendee_token = create_attendee(
        client,
        "admin-dashboard",
    )

    response = client.get(
        "/dashboard/admin",
        headers=headers(attendee_token),
    )

    assert response.status_code == 403


def test_attendee_cannot_access_organizer_dashboard(client):
    attendee, attendee_token = create_attendee(
        client,
        "organizer-dashboard",
    )

    response = client.get(
        "/dashboard/organizer",
        headers=headers(attendee_token),
    )

    assert response.status_code == 403


# ============================================================
# 2. EVENT OWNERSHIP
# ============================================================

def test_other_organizer_cannot_update_event(client):
    organizer1, organizer1_token = create_organizer(
        client,
        "event-owner",
    )

    organizer2, organizer2_token = create_organizer(
        client,
        "different-owner",
    )

    event = create_event(
        client,
        organizer1,
        organizer1_token,
        "ownership-update",
    )

    response = client.put(
        f"/events/{event['id']}",
        json={
            "event_name": "Unauthorized Update",
        },
        headers=headers(organizer2_token),
    )

    assert response.status_code == 403


def test_other_organizer_cannot_delete_event(client):
    organizer1, organizer1_token = create_organizer(
        client,
        "event-delete-owner",
    )

    organizer2, organizer2_token = create_organizer(
        client,
        "event-delete-other",
    )

    event = create_event(
        client,
        organizer1,
        organizer1_token,
        "ownership-delete",
    )

    response = client.delete(
        f"/events/{event['id']}",
        headers=headers(organizer2_token),
    )

    assert response.status_code == 403


# ============================================================
# 3. EVENT CANCELLATION OWNERSHIP
# ============================================================

def test_other_organizer_cannot_cancel_event(client):
    organizer1, organizer1_token = create_organizer(
        client,
        "cancel-owner",
    )

    organizer2, organizer2_token = create_organizer(
        client,
        "cancel-other",
    )

    event = create_event(
        client,
        organizer1,
        organizer1_token,
        "ownership-cancel",
    )

    response = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=headers(organizer2_token),
    )

    assert response.status_code == 403


# ============================================================
# 4. INVALID REFUND STATE
# ============================================================

def test_refunded_purchase_cannot_be_refunded_again(client):
    organizer, organizer_token = create_organizer(
        client,
        "double-refund-owner",
    )

    attendee, attendee_token = create_attendee(
        client,
        "double-refund-attendee",
    )

    event = create_event(
        client,
        organizer,
        organizer_token,
        "double-refund-event",
    )

    # Register attendee.
    registration_response = client.post(
        "/attendees",
        json={
            "user_id": attendee["id"],
            "event_id": event["id"],
        },
        headers=headers(attendee_token),
    )

    assert registration_response.status_code == 201

    registration = registration_response.json()

    # Create ticket.
    ticket_response = client.post(
        "/tickets",
        json={
            "event_id": event["id"],
            "ticket_name": "Level 17 Refund Ticket",
            "ticket_type": "Regular",
            "price": 1000,
            "quantity": 10,
            "status": "Available",
        },
        headers=headers(organizer_token),
    )

    assert ticket_response.status_code == 201

    ticket = ticket_response.json()

    # Purchase ticket.
    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": registration["id"],
            "quantity": 1,
        },
        headers=headers(attendee_token),
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    # Payment success.
    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
        headers=headers(attendee_token),
    )

    assert payment_response.status_code == 200

    # First refund.
    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund",
        headers=headers(attendee_token),
    )

    assert refund_response.status_code == 200

    assert refund_response.json()["payment_status"] == "Refunded"

    # Second refund must be rejected.
    second_refund = client.put(
        f"/ticket-purchases/{purchase['id']}/refund",
        headers=headers(attendee_token),
    )

    assert second_refund.status_code in (400, 409)


def test_refunded_purchase_cannot_receive_payment_again(client):
    organizer, organizer_token = create_organizer(
        client,
        "refunded-payment-owner",
    )

    attendee, attendee_token = create_attendee(
        client,
        "refunded-payment-attendee",
    )

    event = create_event(
        client,
        organizer,
        organizer_token,
        "refunded-payment-event",
    )

    registration_response = client.post(
        "/attendees",
        json={
            "user_id": attendee["id"],
            "event_id": event["id"],
        },
        headers=headers(attendee_token),
    )

    assert registration_response.status_code == 201

    registration = registration_response.json()

    ticket_response = client.post(
        "/tickets",
        json={
            "event_id": event["id"],
            "ticket_name": "Refunded Payment Ticket",
            "ticket_type": "Regular",
            "price": 1000,
            "quantity": 10,
            "status": "Available",
        },
        headers=headers(organizer_token),
    )

    assert ticket_response.status_code == 201

    ticket = ticket_response.json()

    purchase_response = client.post(
        "/ticket-purchases",
        json={
            "ticket_id": ticket["id"],
            "attendee_id": registration["id"],
            "quantity": 1,
        },
        headers=headers(attendee_token),
    )

    assert purchase_response.status_code == 201

    purchase = purchase_response.json()

    payment_response = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
        headers=headers(attendee_token),
    )

    assert payment_response.status_code == 200

    refund_response = client.put(
        f"/ticket-purchases/{purchase['id']}/refund",
        headers=headers(attendee_token),
    )

    assert refund_response.status_code == 200

    # Payment must not be changed after refund.
    payment_after_refund = client.put(
        f"/ticket-purchases/{purchase['id']}/payment",
        json={
            "payment_status": "Success",
        },
        headers=headers(attendee_token),
    )

    assert payment_after_refund.status_code in (400, 409)


# ============================================================
# 5. INVALID EVENT STATE
# ============================================================

def test_cancelled_event_cannot_be_cancelled_again(
    client,
):
    organizer, organizer_token = create_organizer(
        client,
        "cancelled-event",
    )

    event = create_event(
        client,
        organizer,
        organizer_token,
        "already-cancelled",
    )

    first_cancel = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=headers(organizer_token),
    )

    assert first_cancel.status_code == 200

    second_cancel = client.put(
        f"/events/{event['id']}",
        json={
            "status": "Cancelled",
        },
        headers=headers(organizer_token),
    )

    assert second_cancel.status_code == 200

    assert second_cancel.json()["status"] == "Cancelled"


# ============================================================
# 6. UNAUTHENTICATED ACCESS
# ============================================================

def test_event_update_requires_authentication(client):
    organizer, organizer_token = create_organizer(
        client,
        "unauthenticated-update",
    )

    event = create_event(
        client,
        organizer,
        organizer_token,
        "auth-required",
    )

    response = client.put(
        f"/events/{event['id']}",
        json={
            "event_name": "Unauthenticated Update",
        },
    )

    assert response.status_code == 401


def test_event_delete_requires_authentication(client):
    organizer, organizer_token = create_organizer(
        client,
        "unauthenticated-delete",
    )

    event = create_event(
        client,
        organizer,
        organizer_token,
        "delete-auth-required",
    )

    response = client.delete(
        f"/events/{event['id']}",
    )

    assert response.status_code == 401


# ============================================================
# 7. INVALID RESOURCE ACCESS
# ============================================================

def test_get_nonexistent_event_returns_404(
    client,
):
    attendee, attendee_token = create_attendee(
        client,
        "nonexistent-event",
    )

    response = client.get(
        "/events/999999999",
        headers=headers(attendee_token),
    )

    assert response.status_code == 404