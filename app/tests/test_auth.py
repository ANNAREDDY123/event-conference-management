def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Attendee",
            "email": "test_attendee@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test Attendee"
    assert data["email"] == "test_attendee@example.com"
    assert data["role"] == "Attendee"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_duplicate_registration(client):
    # First registration
    first_response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Attendee",
            "email": "test_attendee@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert first_response.status_code == 201

    # Duplicate registration
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Duplicate User",
            "email": "test_attendee@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered"


def test_login_user(client):
    # Register user for this test
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Login Test User",
            "email": "login_user@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "login_user@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login_user@example.com"


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Invalid Password User",
            "email": "invalid_password@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "invalid_password@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_current_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Current User Test",
            "email": "current_user@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "current_user@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "current_user@example.com"
    assert data["role"] == "Attendee"


def test_refresh_token(client):
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Refresh Token User",
            "email": "refresh_user@example.com",
            "password": "password123",
            "role": "Attendee",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh_user@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"