"""Business logic for the expense management app."""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Optional

from .currency import convert, list_supported_currencies, validate_currency
from .models import Expense, Wallet


class WalletExistsError(ValueError):
    """Raised when attempting to create a wallet that already exists."""


class WalletNotFoundError(ValueError):
    """Raised when a wallet cannot be located."""


class ExpenseManager:
    """Encapsulates core operations for managing wallets and expenses."""

    def __init__(self, data: Dict[str, List[Dict]] | None = None) -> None:
        payload = data or {"wallets": []}
        self.wallets: Dict[str, Wallet] = {}
        for wallet_data in payload.get("wallets", []):
            wallet = Wallet(
                name=wallet_data["name"],
                currency=wallet_data["currency"],
                balance=wallet_data.get("balance", 0.0),
                expenses=[
                    Expense(
                        description=expense["description"],
                        amount=expense["amount"],
                        category=expense.get("category", "uncategorized"),
                    )
                    for expense in wallet_data.get("expenses", [])
                ],
            )
            self.wallets[wallet.name.lower()] = wallet

    # ------------------------------------------------------------------
    # Wallet operations
    # ------------------------------------------------------------------
    def create_wallet(self, name: str, currency: str, balance: float = 0.0) -> Wallet:
        key = name.lower()
        if key in self.wallets:
            raise WalletExistsError(f"A wallet named '{name}' already exists.")
        validate_currency(currency)
        wallet = Wallet(name=name, currency=currency, balance=balance)
        self.wallets[key] = wallet
        return wallet

    def get_wallet(self, name: str) -> Wallet:
        key = name.lower()
        if key not in self.wallets:
            raise WalletNotFoundError(f"Wallet '{name}' not found.")
        return self.wallets[key]

    def list_wallets(self) -> Iterable[Wallet]:
        return self.wallets.values()

    # ------------------------------------------------------------------
    # Expense operations
    # ------------------------------------------------------------------
    def add_expense(self, wallet_name: str, description: str, amount: float, category: str) -> Expense:
        wallet = self.get_wallet(wallet_name)
        expense = Expense(description=description, amount=amount, category=category)
        wallet.add_expense(expense)
        return expense

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, List[Dict]]:
        return {
            "wallets": [
                {
                    "name": wallet.name,
                    "currency": wallet.currency,
                    "balance": wallet.balance,
                    "expenses": [asdict(expense) for expense in wallet.expenses],
                }
                for wallet in self.list_wallets()
            ]
        }

    def consolidated_dashboard(self, target_currency: str) -> Dict[str, float | List[Dict[str, float | str]]]:
        validate_currency(target_currency)
        total_balance = 0.0
        total_spent = 0.0
        wallets_summary: List[Dict[str, float | str]] = []

        for wallet in self.list_wallets():
            balance_converted = convert(wallet.balance, wallet.currency, target_currency)
            spent_converted = convert(wallet.total_spent(), wallet.currency, target_currency)
            total_balance += balance_converted
            total_spent += spent_converted
            wallets_summary.append(
                {
                    "name": wallet.name,
                    "currency": wallet.currency,
                    "balance": wallet.balance,
                    "balance_in_target": balance_converted,
                    "total_spent": wallet.total_spent(),
                    "total_spent_in_target": spent_converted,
                }
            )

        return {
            "target_currency": target_currency,
            "total_balance": total_balance,
            "total_spent": total_spent,
            "net_position": total_balance - total_spent,
            "wallets": wallets_summary,
            "supported_currencies": list_supported_currencies(),
        }

    def wallet_report(self, wallet_name: str, target_currency: Optional[str] = None) -> Dict[str, float | str | List[Dict[str, float | str]]]:
        wallet = self.get_wallet(wallet_name)
        target = target_currency or wallet.currency
        validate_currency(target)
        return {
            "wallet": wallet.name,
            "wallet_currency": wallet.currency,
            "balance": wallet.balance,
            "balance_in_target": convert(wallet.balance, wallet.currency, target),
            "expenses": [
                {
                    "description": expense.description,
                    "amount": expense.amount,
                    "category": expense.category,
                    "amount_in_target": convert(expense.amount, wallet.currency, target),
                }
                for expense in wallet.expenses
            ],
            "target_currency": target,
        }
