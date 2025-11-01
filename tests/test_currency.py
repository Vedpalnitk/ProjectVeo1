from expense_manager.currency import convert, validate_currency


def test_validate_currency_accepts_supported_codes():
    # Should not raise
    validate_currency("USD")
    validate_currency("EUR")


def test_convert_between_supported_currencies():
    amount_usd = 100
    converted = convert(amount_usd, "USD", "EUR")
    # Using rate 0.92, so 100 USD -> 92 EUR
    assert round(converted, 2) == 92.0


def test_convert_round_trip():
    amount = 50
    converted = convert(amount, "GBP", "JPY")
    back = convert(converted, "JPY", "GBP")
    assert round(back, 2) == round(amount, 2)
