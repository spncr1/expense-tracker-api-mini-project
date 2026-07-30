from datetime import UTC, datetime, timedelta

from jose import jwt

from app.core.config import get_settings
from app.users.repository import get_user_by_email
from tests.conftest import register_and_login


def test_register_creates_user_without_exposing_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "hashed_password" not in response.json()


def test_register_rejects_duplicate_email(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_login_returns_bearer_token(client):
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"].count(".") == 2


def test_login_rejects_bad_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_me_requires_valid_token(client):
    missing_token = client.get("/auth/me")
    invalid_token = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert missing_token.status_code == 401
    assert invalid_token.status_code == 401


def test_me_rejects_expired_token(client):
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_me_rejects_token_for_deleted_user(client, db_session):
    headers = register_and_login(client, "deleted@example.com")
    user = get_user_by_email(db_session, "deleted@example.com")

    db_session.delete(user)
    db_session.commit()

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401


def test_me_returns_current_user(client):
    headers = register_and_login(client, "current@example.com")

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "current@example.com"
