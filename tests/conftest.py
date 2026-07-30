import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import app.expenses.models
import app.users.models


@pytest.fixture
def testing_session_local():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )


@pytest.fixture
def db_session(testing_session_local):
    db = testing_session_local()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(testing_session_local):
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app) as test_client:
        yield test_client

    fastapi_app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str = "user@example.com") -> dict[str, str]:
    password = "password123"
    client.post(
        "/auth/register",
        json={
            "name": email.split("@")[0],
            "email": email,
            "password": password,
        },
    )
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_expense(
    client: TestClient,
    headers: dict[str, str],
    title: str = "Groceries run",
    amount: str = "42.50",
    category: str = "Groceries",
    expense_date: str = "2026-07-30",
):
    return client.post(
        "/expenses",
        headers=headers,
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "expense_date": expense_date,
        },
    )
