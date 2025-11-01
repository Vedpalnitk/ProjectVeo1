from expense_manager.manager import ExpenseManager


def create_sample_manager():
    manager = ExpenseManager()
    manager.create_wallet("Personal", "USD", balance=1000)
    manager.create_wallet("Travel", "EUR", balance=500)
    manager.add_expense("Personal", "Groceries", 120, "food")
    manager.add_expense("Travel", "Hotel", 200, "lodging")
    return manager


def test_consolidated_dashboard():
    manager = create_sample_manager()
    dashboard = manager.consolidated_dashboard("USD")
    assert dashboard["target_currency"] == "USD"
    assert len(dashboard["wallets"]) == 2
    personal = next(w for w in dashboard["wallets"] if w["name"] == "Personal")
    assert personal["total_spent"] == 120
    assert dashboard["total_spent"] > 120  # includes Travel wallet spent converted to USD


def test_wallet_report_conversion():
    manager = create_sample_manager()
    report = manager.wallet_report("Travel", target_currency="USD")
    assert report["wallet"] == "Travel"
    assert report["target_currency"] == "USD"
    assert len(report["expenses"]) == 1
    assert report["expenses"][0]["amount_in_target"] > 0
