"""Sample data helpers for demonstrating the CLI preview."""
from __future__ import annotations

from typing import Any, Dict, List


def load_demo_data() -> Dict[str, List[Dict[str, Any]]]:
    """Return a representative dataset with multiple wallets and expenses.

    The structure mirrors what the application persists on disk, allowing the
    preview command to showcase realistic consolidated totals without requiring
    the user to manually create wallets first.
    """

    return {
        "wallets": [
            {
                "name": "Personal",
                "currency": "USD",
                "balance": 1200.0,
                "expenses": [
                    {
                        "description": "Rent",
                        "amount": 700.0,
                        "category": "housing",
                    },
                    {
                        "description": "Groceries",
                        "amount": 150.0,
                        "category": "food",
                    },
                ],
            },
            {
                "name": "Travel",
                "currency": "EUR",
                "balance": 500.0,
                "expenses": [
                    {
                        "description": "Flights",
                        "amount": 200.0,
                        "category": "travel",
                    }
                ],
            },
            {
                "name": "Savings",
                "currency": "JPY",
                "balance": 100000.0,
                "expenses": [],
            },
        ]
    }

