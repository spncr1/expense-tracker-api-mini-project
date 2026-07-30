from datetime import UTC, datetime, timedelta

from tests.conftest import create_expense, register_and_login


def test_create_expense(client):
    headers = register_and_login(client)

    response = create_expense(client, headers)

    assert response.status_code == 201
    assert response.json()["title"] == "Groceries run"
    assert response.json()["amount"] == "42.50"
    assert response.json()["category"] == "Groceries"
    assert response.json()["user_id"] == 1


def test_list_expenses_returns_paginated_shape(client):
    headers = register_and_login(client)
    create_expense(client, headers)

    response = client.get("/expenses", headers=headers)

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["page"] == 1
    assert response.json()["limit"] == 10
    assert response.json()["total"] == 1


def test_get_update_and_delete_expense(client):
    headers = register_and_login(client)
    created = create_expense(client, headers)
    expense_id = created.json()["id"]

    fetched = client.get(f"/expenses/{expense_id}", headers=headers)
    updated = client.put(
        f"/expenses/{expense_id}",
        headers=headers,
        json={
            "title": "Updated expense",
            "amount": "50.00",
        },
    )
    deleted = client.delete(f"/expenses/{expense_id}", headers=headers)
    missing_after_delete = client.get(f"/expenses/{expense_id}", headers=headers)

    assert fetched.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated expense"
    assert updated.json()["amount"] == "50.00"
    assert deleted.status_code == 204
    assert missing_after_delete.status_code == 404


def test_user_cannot_access_another_users_expense(client):
    user_a_headers = register_and_login(client, "user-a@example.com")
    user_b_headers = register_and_login(client, "user-b@example.com")
    created = create_expense(client, user_a_headers)
    expense_id = created.json()["id"]

    user_b_list = client.get("/expenses", headers=user_b_headers)
    user_b_get = client.get(f"/expenses/{expense_id}", headers=user_b_headers)
    user_b_update = client.put(
        f"/expenses/{expense_id}",
        headers=user_b_headers,
        json={"title": "Not yours"},
    )
    user_b_delete = client.delete(f"/expenses/{expense_id}", headers=user_b_headers)
    user_a_still_gets = client.get(f"/expenses/{expense_id}", headers=user_a_headers)

    assert user_b_list.status_code == 200
    assert user_b_list.json()["total"] == 0
    assert user_b_get.status_code == 404
    assert user_b_update.status_code == 404
    assert user_b_delete.status_code == 404
    assert user_a_still_gets.status_code == 200


def test_expense_filters(client):
    headers = register_and_login(client)
    today = datetime.now(UTC).date()
    fixtures = [
        ("today groceries", "Groceries", today),
        ("six days utilities", "Utilities", today - timedelta(days=6)),
        ("twenty days health", "Health", today - timedelta(days=20)),
        ("sixty days groceries", "Groceries", today - timedelta(days=60)),
        ("one hundred days leisure", "Leisure", today - timedelta(days=100)),
    ]

    for title, category, expense_date in fixtures:
        create_expense(
            client,
            headers,
            title=title,
            category=category,
            expense_date=expense_date.isoformat(),
        )

    custom_start = (today - timedelta(days=65)).isoformat()
    custom_end = (today - timedelta(days=15)).isoformat()

    assert client.get("/expenses?category=Groceries", headers=headers).json()["total"] == 2
    assert client.get("/expenses?period=past_week", headers=headers).json()["total"] == 2
    assert client.get("/expenses?period=past_month", headers=headers).json()["total"] == 3
    assert client.get("/expenses?period=last_3_months", headers=headers).json()["total"] == 4
    assert (
        client.get(
            f"/expenses?period=custom&start_date={custom_start}&end_date={custom_end}",
            headers=headers,
        ).json()["total"]
        == 2
    )


def test_expense_filter_errors(client):
    headers = register_and_login(client)

    missing_custom_dates = client.get("/expenses?period=custom", headers=headers)
    backwards_dates = client.get(
        "/expenses?start_date=2026-07-30&end_date=2026-07-29",
        headers=headers,
    )

    assert missing_custom_dates.status_code == 400
    assert backwards_dates.status_code == 400


def test_expense_pagination(client):
    headers = register_and_login(client)

    for index in range(12):
        create_expense(
            client,
            headers,
            title=f"Expense {index + 1}",
            category="Groceries" if index % 2 == 0 else "Health",
        )

    page_one = client.get("/expenses?page=1&limit=5", headers=headers).json()
    page_two = client.get("/expenses?page=2&limit=5", headers=headers).json()
    page_three = client.get("/expenses?page=3&limit=5", headers=headers).json()
    filtered = client.get(
        "/expenses?category=Groceries&page=1&limit=3",
        headers=headers,
    ).json()

    assert len(page_one["items"]) == 5
    assert page_one["total"] == 12
    assert len(page_two["items"]) == 5
    assert page_two["total"] == 12
    assert len(page_three["items"]) == 2
    assert page_three["total"] == 12
    assert len(filtered["items"]) == 3
    assert filtered["total"] == 6


def test_expense_validation_errors(client):
    headers = register_and_login(client)
    created = create_expense(client, headers)
    expense_id = created.json()["id"]

    empty_update = client.put(f"/expenses/{expense_id}", headers=headers, json={})
    invalid_amount = create_expense(client, headers, amount="0")
    missing_title = client.post(
        "/expenses",
        headers=headers,
        json={
            "amount": "10.00",
            "category": "Groceries",
            "expense_date": "2026-07-30",
        },
    )
    unknown_category = client.get("/expenses?category=Food", headers=headers)
    bad_page = client.get("/expenses?page=0", headers=headers)

    assert empty_update.status_code == 400
    assert invalid_amount.status_code == 422
    assert missing_title.status_code == 422
    assert unknown_category.status_code == 422
    assert bad_page.status_code == 422
