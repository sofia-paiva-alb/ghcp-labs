"""
Lab 6 — Agent Mode
===================
A CLI expense tracker with multiple modules. Participants use Agent Mode
for autonomous multi-step tasks: adding features, refactoring across files,
and fixing cross-module bugs.
"""

import json
import csv
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from typing import Optional


class Category(Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SHOPPING = "shopping"
    OTHER = "other"


@dataclass
class Expense:
    amount: float
    category: Category
    description: str
    date: date = field(default_factory=date.today)
    tags: list[str] = field(default_factory=list)
    expense_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "expense_id": self.expense_id,
            "amount": self.amount,
            "category": self.category.value,
            "description": self.description,
            "date": self.date.isoformat(),
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(
            expense_id=data.get("expense_id"),
            amount=float(data["amount"]),
            category=Category(data["category"]),
            description=data["description"],
            date=date.fromisoformat(data["date"]),
            tags=data.get("tags", []),
        )


@dataclass
class Budget:
    category: Category
    monthly_limit: float
    alerts_enabled: bool = True


class ExpenseStore:
    """Persists expenses to a JSON file."""

    def __init__(self, filepath: str = "expenses.json"):
        self.filepath = Path(filepath)
        self._expenses: list[Expense] = []
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, encoding="utf-8") as f:
                data = json.load(f)
            self._expenses = [Expense.from_dict(d) for d in data]
            if self._expenses:
                self._next_id = max(e.expense_id or 0 for e in self._expenses) + 1

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self._expenses], f, indent=2)

    def add(self, expense: Expense) -> Expense:
        expense.expense_id = self._next_id
        self._next_id += 1
        self._expenses.append(expense)
        self._save()
        return expense

    def get(self, expense_id: int) -> Optional[Expense]:
        for e in self._expenses:
            if e.expense_id == expense_id:
                return e
        return None

    def delete(self, expense_id: int) -> bool:
        for i, e in enumerate(self._expenses):
            if e.expense_id == expense_id:
                self._expenses.pop(i)
                self._save()
                return True
        return False

    def list_all(self) -> list[Expense]:
        return list(self._expenses)

    def filter_by_category(self, category: Category) -> list[Expense]:
        return [e for e in self._expenses if e.category == category]

    def filter_by_date_range(self, start: date, end: date) -> list[Expense]:
        return [e for e in self._expenses if start <= e.date <= end]

    def total_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for e in self._expenses:
            cat = e.category.value
            totals[cat] = totals.get(cat, 0) + e.amount
        return totals


class ReportGenerator:
    """Generates expense reports."""

    def __init__(self, store: ExpenseStore):
        self.store = store

    def monthly_summary(self, year: int, month: int) -> dict:
        expenses = [
            e for e in self.store.list_all()
            if e.date.year == year and e.date.month == month
        ]
        total = sum(e.amount for e in expenses)
        by_category = {}
        for e in expenses:
            cat = e.category.value
            by_category[cat] = by_category.get(cat, 0) + e.amount

        return {
            "period": f"{year}-{month:02d}",
            "total_expenses": round(total, 2),
            "transaction_count": len(expenses),
            "by_category": by_category,
            "daily_average": round(total / 30, 2) if expenses else 0,
        }

    def export_csv(self, filepath: str, expenses: Optional[list[Expense]] = None) -> int:
        """Export expenses to CSV. Returns count of rows written."""
        items = expenses or self.store.list_all()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["expense_id", "amount", "category", "description", "date", "tags"])
            writer.writeheader()
            for e in items:
                row = e.to_dict()
                row["tags"] = ",".join(row["tags"])
                writer.writerow(row)
        return len(items)


class BudgetTracker:
    """Tracks spending against budgets."""

    def __init__(self, store: ExpenseStore):
        self.store = store
        self._budgets: dict[str, Budget] = {}

    def set_budget(self, budget: Budget) -> None:
        self._budgets[budget.category.value] = budget

    def get_budget(self, category: Category) -> Optional[Budget]:
        return self._budgets.get(category.value)

    def check_budget(self, category: Category, year: int, month: int) -> dict:
        budget = self.get_budget(category)
        if budget is None:
            return {"status": "no_budget", "category": category.value}

        expenses = [
            e for e in self.store.list_all()
            if e.category == category and e.date.year == year and e.date.month == month
        ]
        spent = sum(e.amount for e in expenses)
        remaining = budget.monthly_limit - spent
        pct_used = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        return {
            "category": category.value,
            "budget": budget.monthly_limit,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percent_used": round(pct_used, 1),
            "over_budget": remaining < 0,
        }
