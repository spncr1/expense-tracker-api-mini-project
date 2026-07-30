import enum
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.expenses.models import ExpenseCategory


class ExpensePeriod(str, enum.Enum):
    PAST_WEEK = "past_week"
    PAST_MONTH = "past_month"
    LAST_3_MONTHS = "last_3_months"
    CUSTOM = "custom"


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: ExpenseCategory
    expense_date: date
    description: str | None = None


class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: ExpenseCategory | None = None
    expense_date: date | None = None
    description: str | None = None


class ExpenseRead(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: ExpenseCategory
    expense_date: date
    description: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListRead(BaseModel):
    items: list[ExpenseRead]
    page: int
    limit: int
    total: int
