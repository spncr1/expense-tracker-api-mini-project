from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.expenses.models import Expense, ExpenseCategory
from app.expenses.schemas import ExpenseCreate, ExpenseUpdate


def create_expense(
    db: Session,
    expense_data: ExpenseCreate,
    user_id: int,
) -> Expense:
    expense = Expense(
        **expense_data.model_dump(),
        user_id=user_id,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def list_expenses(
    db: Session,
    user_id: int,
    category: ExpenseCategory | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Expense], int]:
    statement = select(Expense).where(Expense.user_id == user_id)
    count_statement = select(func.count()).select_from(Expense).where(
        Expense.user_id == user_id
    )

    if category is not None:
        statement = statement.where(Expense.category == category)
        count_statement = count_statement.where(Expense.category == category)

    if start_date is not None:
        statement = statement.where(Expense.expense_date >= start_date)
        count_statement = count_statement.where(Expense.expense_date >= start_date)

    if end_date is not None:
        statement = statement.where(Expense.expense_date <= end_date)
        count_statement = count_statement.where(Expense.expense_date <= end_date)

    offset = (page - 1) * limit
    total = db.scalar(count_statement) or 0
    statement = (
        statement
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(db.scalars(statement)), total


def get_expense_by_id(
    db: Session,
    expense_id: int,
    user_id: int,
) -> Expense | None:
    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == user_id,
    )

    return db.scalar(statement)


def update_expense(
    db: Session,
    expense: Expense,
    expense_data: ExpenseUpdate,
) -> Expense:
    update_data = expense_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()
