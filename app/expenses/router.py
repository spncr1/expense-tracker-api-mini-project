from typing import Annotated

from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.exceptions import bad_request_error, not_found_error
from app.database.session import get_db
from app.expenses.models import ExpenseCategory
from app.expenses.schemas import (
    ExpenseCreate,
    ExpenseListRead,
    ExpensePeriod,
    ExpenseRead,
    ExpenseUpdate,
)
from app.expenses.service import (
    create_user_expense,
    delete_user_expense,
    get_user_expense,
    list_user_expenses,
    update_user_expense,
)
from app.users.models import User


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return create_user_expense(db, expense_data, current_user.id)


@router.get("", response_model=ExpenseListRead)
async def get_expenses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    category: ExpenseCategory | None = Query(default=None),
    period: ExpensePeriod | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    try:
        items, total = list_user_expenses(
            db,
            current_user.id,
            category=category,
            period=period,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit,
        )
    except ValueError as error:
        raise bad_request_error(str(error)) from error

    return ExpenseListRead(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    expense = get_user_expense(db, expense_id, current_user.id)

    if expense is None:
        raise not_found_error("Expense")

    return expense


@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        expense = update_user_expense(db, expense_id, expense_data, current_user.id)
    except ValueError as error:
        raise bad_request_error(str(error)) from error

    if expense is None:
        raise not_found_error("Expense")

    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    was_deleted = delete_user_expense(db, expense_id, current_user.id)

    if not was_deleted:
        raise not_found_error("Expense")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
