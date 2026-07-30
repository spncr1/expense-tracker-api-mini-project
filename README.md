# Expense Tracker API

An API for tracking personal expenses, built with Python, FastAPI, SQLAlchemy,
Alembic, SQLite, JWT authentication, and Pytest.

## Project Brief

```text
https://roadmap.sh/projects/expense-tracker-api
```

## Features

- Register a user.
- Log in and receive a JWT access token.
- Protect expense routes with bearer-token authentication.
- Create, list, view, update, and delete expenses.
- Keep each user's expenses private.
- Filter expenses by category and date period.
- Paginate expense results.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```env
APP_NAME="Expense Tracker API"
DATABASE_URL="sqlite:///./expense_tracker.db"
JWT_SECRET_KEY="replace-this-with-a-generated-secret"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a local JWT secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Paste the generated value into `JWT_SECRET_KEY` in the .env file.

## Database

Run migrations:

```bash
alembic upgrade head
```

The local SQLite database is:

```text
expense_tracker.db
```

## Run

Start the development server:

```bash
uvicorn app.main:app --reload
```

Local API server:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

Health:

```text
GET /health
```

Auth:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Expenses:

```text
POST   /expenses
GET    /expenses
GET    /expenses/{expense_id}
PUT    /expenses/{expense_id}
DELETE /expenses/{expense_id}
```

`GET /expenses` supports:

```text
category
period=past_week|past_month|last_3_months|custom
start_date
end_date
page
limit
```

Protected routes require:

```text
Authorization: Bearer <access_token>
```

## Data Model

The API has two main models:

- `User`: a person who can register, log in, and own expenses.
- `Expense`: one spending record that belongs to one user.

Relationship:

```text
User has many Expenses
Expense belongs to one User
```

Expense categories:

```text
Groceries
Leisure
Electronics
Utilities
Clothing
Health
Others
```

## Tests

Run the test suite:

```bash
pytest
```
