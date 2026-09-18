# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def register_user(client, email: str):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Speaker Test User",
            "email": email,
            "password": "TestPassword123",
            "role": "Attendee",
        },
    )

    assert response.status_code == 201


def login_user(client, email: str):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
    }


def speaker_payload(
    email: str = "john.smith@example.com",
):
    return {
        "name": "John Smith",
        "email": email,
        "phone": "9876543210",
        "bio": "Technology speaker and developer",
        "expertise": "Python, FastAPI, Backend Development",
        "company": "Tech Solutions",
        "experience": 10,
        "is_active": True,
    }


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_create_speaker(client):
    email = "speaker_user@example.com"

    register_user(client, email)
    token = login_user(client, email)

    response = client.post(
        "/speakers",
        json=speaker_payload(
            "create.speaker@example.com"
        ),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "John Smith"
    assert data["email"] == "create.speaker@example.com"
    assert data["experience"] == 10
    assert data["is_active"] is True


def test_get_speakers(client):
    email = "speaker_list_user@example.com"

    register_user(client, email)
    token = login_user(client, email)

    response = client.post(
        "/speakers",
        json=speaker_payload(
            "list.speaker@example.com"
        ),
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    response = client.get(
        "/speakers",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    speakers = response.json()

    assert isinstance(speakers, list)
    assert len(speakers) >= 1


def test_get_speaker(client):
    email = "speaker_get_user@example.com"

    register_user(client, email)
    token = login_user(client, email)

    create_response = client.post(
        "/speakers",
        json=speaker_payload(
            "get.speaker@example.com"
        ),
        headers=auth_headers(token),
    )

    assert create_response.status_code == 201

    speaker_id = create_response.json()["id"]

    response = client.get(
        f"/speakers/{speaker_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == speaker_id
    assert data["name"] == "John Smith"
    assert data["email"] == "get.speaker@example.com"


def test_get_nonexistent_speaker(client):
    email = "speaker_not_found@example.com"

    register_user(client, email)
    token = login_user(client, email)

    response = client.get(
        "/speakers/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Speaker not found"


def test_update_speaker(client):
    email = "speaker_update_user@example.com"

    register_user(client, email)
    token = login_user(client, email)

    create_response = client.post(
        "/speakers",
        json=speaker_payload(
            "update.speaker@example.com"
        ),
        headers=auth_headers(token),
    )

    assert create_response.status_code == 201

    speaker_id = create_response.json()["id"]

    response = client.put(
        f"/speakers/{speaker_id}",
        json={
            "company": "Updated Tech Company",
            "experience": 12,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["company"] == "Updated Tech Company"
    assert data["experience"] == 12


def test_duplicate_speaker_email(client):
    email = "speaker_duplicate@example.com"

    register_user(client, email)
    token = login_user(client, email)

    first_response = client.post(
        "/speakers",
        json=speaker_payload(
            "duplicate.speaker@example.com"
        ),
        headers=auth_headers(token),
    )

    assert first_response.status_code == 201

    duplicate_payload = speaker_payload(
        "duplicate.speaker@example.com"
    )

    duplicate_payload["name"] = "Another Speaker"

    response = client.post(
        "/speakers",
        json=duplicate_payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Speaker with this email already exists"
    )


def test_update_speaker_duplicate_email(client):
    email = "speaker_update_duplicate@example.com"

    register_user(client, email)
    token = login_user(client, email)

    first_payload = speaker_payload(
        "first.speaker@example.com"
    )

    second_payload = speaker_payload(
        "second.speaker@example.com"
    )

    second_payload["name"] = "Second Speaker"

    first_response = client.post(
        "/speakers",
        json=first_payload,
        headers=auth_headers(token),
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/speakers",
        json=second_payload,
        headers=auth_headers(token),
    )

    assert second_response.status_code == 201

    second_id = second_response.json()["id"]

    response = client.put(
        f"/speakers/{second_id}",
        json={
            "email": "first.speaker@example.com",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Speaker with this email already exists"
    )


def test_invalid_speaker_experience(client):
    email = "speaker_invalid_experience@example.com"

    register_user(client, email)
    token = login_user(client, email)

    payload = speaker_payload(
        "invalid.experience@example.com"
    )

    payload["experience"] = -5

    response = client.post(
        "/speakers",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_invalid_speaker_email(client):
    email = "speaker_invalid_email@example.com"

    register_user(client, email)
    token = login_user(client, email)

    payload = speaker_payload(
        "valid.email@example.com"
    )

    payload["email"] = "invalid-email"

    response = client.post(
        "/speakers",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422