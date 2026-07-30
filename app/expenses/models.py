import enum
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.users.models import User


class ExpenseCategory(str, enum.Enum):
    GROCERIES = "Groceries"
    LEISURE = "Leisure"
    ELECTRONICS = "Electronics"
    UTILITIES = "Utilities"
    CLOTHING = "Clothing"
    HEALTH = "Health"
    OTHERS = "Others"


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(
            ExpenseCategory,
            values_callable=lambda categories: [category.value for category in categories],
        ),
        nullable=False,
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="expenses")
