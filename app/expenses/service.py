from datetime import UTC, date, datetime, timedelta

from sqlalchemy.orm import Session

from app.expenses.models import Expense, ExpenseCategory
from app.expenses.repository import (
    create_expense,
    delete_expense,
    get_expense_by_id,
    list_expenses,
    update_expense,
)
from app.expenses.schemas import ExpenseCreate, ExpensePeriod, ExpenseUpdate


def create_user_expense(
    db: Session,
    expense_data: ExpenseCreate,
    user_id: int,
) -> Expense:
    return create_expense(db, expense_data, user_id)


def _resolve_date_range(
    period: ExpensePeriod | None,
    start_date: date | None,
    end_date: date | None,
) -> tuple[date | None, date | None]:
    today = datetime.now(UTC).date()

    if period is None:
        return start_date, end_date

    if period == ExpensePeriod.PAST_WEEK:
        return today - timedelta(days=7), today

    if period == ExpensePeriod.PAST_MONTH:
        return today - timedelta(days=30), today

    if period == ExpensePeriod.LAST_3_MONTHS:
        return today - timedelta(days=90), today

    if start_date is None or end_date is None:
        raise ValueError("Custom period requires start_date and end_date")

    return start_date, end_date


def list_user_expenses(
    db: Session,
    user_id: int,
    category: ExpenseCategory | None = None,
    period: ExpensePeriod | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Expense], int]:
    resolved_start_date, resolved_end_date = _resolve_date_range(
        period,
        start_date,
        end_date,
    )

    if (
        resolved_start_date is not None
        and resolved_end_date is not None
        and resolved_start_date > resolved_end_date
    ):
        raise ValueError("start_date cannot be after end_date")

    return list_expenses(
        db,
        user_id,
        category=category,
        start_date=resolved_start_date,
        end_date=resolved_end_date,
        page=page,
        limit=limit,
    )


def get_user_expense(
    db: Session,
    expense_id: int,
    user_id: int,
) -> Expense | None:
    # Looking up by both expense id and user id keeps other users' expenses hidden.
    return get_expense_by_id(db, expense_id, user_id)


def update_user_expense(
    db: Session,
    expense_id: int,
    expense_data: ExpenseUpdate,
    user_id: int,
) -> Expense | None:
    if not expense_data.model_fields_set:
        raise ValueError("At least one expense field must be provided")

    expense = get_user_expense(db, expense_id, user_id)

    if expense is None:
        return None

    return update_expense(db, expense, expense_data)


def delete_user_expense(
    db: Session,
    expense_id: int,
    user_id: int,
) -> bool:
    expense = get_user_expense(db, expense_id, user_id)

    if expense is None:
        return False

    delete_expense(db, expense)
    return True
