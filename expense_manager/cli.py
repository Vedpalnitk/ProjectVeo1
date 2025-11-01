"""Command line interface for the expense management app."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from .currency import list_supported_currencies
from .manager import ExpenseManager
from .sample_data import load_demo_data
from .storage import load_data, resolve_data_file, save_data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Expense management app supporting multiple wallets and a consolidated dashboard."
        )
    )
    parser.add_argument(
        "--data-file",
        help="Path to the data file (defaults to ./expense_data.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_wallet = subparsers.add_parser("create-wallet", help="Create a new wallet")
    create_wallet.add_argument("name", help="Name of the wallet")
    create_wallet.add_argument("currency", help="Currency code, e.g. USD")
    create_wallet.add_argument(
        "--balance",
        type=float,
        default=0.0,
        help="Initial balance for the wallet",
    )

    add_expense = subparsers.add_parser("add-expense", help="Add an expense to a wallet")
    add_expense.add_argument("wallet", help="Name of the wallet")
    add_expense.add_argument("amount", type=float, help="Amount of the expense")
    add_expense.add_argument("description", help="Description of the expense")
    add_expense.add_argument(
        "--category",
        default="general",
        help="Category for the expense",
    )

    subparsers.add_parser("list-wallets", help="List wallets and balances")

    dashboard = subparsers.add_parser(
        "dashboard", help="Show consolidated dashboard in a target currency"
    )
    dashboard.add_argument(
        "currency",
        help="Target currency for the dashboard",
    )

    preview = subparsers.add_parser(
        "preview",
        help=(
            "Quickly preview the consolidated dashboard using an optional target currency"
        ),
    )
    preview.add_argument(
        "--currency",
        default="USD",
        help="Target currency for the preview (defaults to USD)",
    )
    preview.add_argument(
        "--demo",
        action="store_true",
        help=(
            "Preview the consolidated dashboard using built-in sample data "
            "without reading or writing any files"
        ),
    )

    wallet_report = subparsers.add_parser("wallet-report", help="Show details for a wallet")
    wallet_report.add_argument("wallet", help="Name of the wallet")
    wallet_report.add_argument(
        "--currency",
        help="Optional target currency for conversion",
    )

    subparsers.add_parser("supported-currencies", help="List supported currency codes")

    return parser


def _load_manager(args: argparse.Namespace) -> ExpenseManager:
    data_file = resolve_data_file(args.data_file)
    data = load_data(data_file)
    return ExpenseManager(data=data)


def _persist(manager: ExpenseManager, args: argparse.Namespace) -> None:
    data_file = resolve_data_file(args.data_file)
    save_data(manager.to_dict(), data_file)


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    demo_mode = args.command == "preview" and getattr(args, "demo", False)
    manager = (
        ExpenseManager(data=load_demo_data()) if demo_mode else _load_manager(args)
    )

    if args.command == "create-wallet":
        wallet = manager.create_wallet(args.name, args.currency, balance=args.balance)
        _persist(manager, args)
        _print_json({"message": f"Wallet '{wallet.name}' created."})
    elif args.command == "add-expense":
        expense = manager.add_expense(args.wallet, args.description, args.amount, args.category)
        _persist(manager, args)
        _print_json({
            "message": f"Added expense '{expense.description}' to wallet '{args.wallet}'.",
            "expense": {
                "description": expense.description,
                "amount": expense.amount,
                "category": expense.category,
            },
        })
    elif args.command == "list-wallets":
        wallets = [
            {
                "name": wallet.name,
                "currency": wallet.currency,
                "balance": wallet.balance,
                "expenses": len(wallet.expenses),
            }
            for wallet in manager.list_wallets()
        ]
        _print_json({"wallets": wallets})
    elif args.command == "dashboard":
        dashboard = manager.consolidated_dashboard(args.currency)
        _print_json(dashboard)
    elif args.command == "wallet-report":
        report = manager.wallet_report(args.wallet, target_currency=args.currency)
        _print_json(report)
    elif args.command == "supported-currencies":
        _print_json({"supported_currencies": list_supported_currencies()})
    elif args.command == "preview":
        target = args.currency.upper()
        dashboard = manager.consolidated_dashboard(target)
        summary = {
            "target_currency": target,
            "total_balance": dashboard["total_balance"],
            "total_spent": dashboard["total_spent"],
            "net_position": dashboard["net_position"],
            "using_demo_data": demo_mode,
        }
        _print_json({"preview": summary})
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
