"""Data models for wallets and expenses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Expense:
    description: str
    amount: float
    category: str


@dataclass
class Wallet:
    name: str
    currency: str
    balance: float = 0.0
    expenses: List[Expense] = field(default_factory=list)

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)
        self.balance -= expense.amount

    def total_spent(self) -> float:
        return sum(exp.amount for exp in self.expenses)
