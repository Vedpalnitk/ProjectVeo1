"""Utilities for working with currency conversion."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


SUPPORTED_CURRENCIES = {
    "USD": 1.0,      # US Dollar
    "EUR": 0.92,     # Euro
    "GBP": 0.81,     # British Pound
    "JPY": 140.0,    # Japanese Yen
    "AUD": 1.5,      # Australian Dollar
}

BASE_CURRENCY = "USD"


@dataclass(frozen=True)
class ConversionRate:
    """Represents a conversion rate relative to the base currency."""

    currency: str
    rate: float


class CurrencyNotSupportedError(ValueError):
    """Raised when an unsupported currency code is provided."""


def validate_currency(currency: str) -> None:
    """Ensure the currency is supported.

    Args:
        currency: ISO-style currency code to validate.

    Raises:
        CurrencyNotSupportedError: If the currency is not supported by the app.
    """

    if currency not in SUPPORTED_CURRENCIES:
        supported = ", ".join(sorted(SUPPORTED_CURRENCIES))
        raise CurrencyNotSupportedError(
            f"Currency '{currency}' is not supported. Supported currencies: {supported}."
        )


def get_rate(currency: str) -> ConversionRate:
    """Return the conversion rate for the given currency relative to the base currency."""
    validate_currency(currency)
    return ConversionRate(currency=currency, rate=SUPPORTED_CURRENCIES[currency])


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert an amount between two supported currencies.

    Args:
        amount: The amount in ``from_currency`` to convert.
        from_currency: Currency code of the original amount.
        to_currency: Currency code to convert the amount into.

    Returns:
        The converted amount expressed in ``to_currency``.
    """

    validate_currency(from_currency)
    validate_currency(to_currency)
    if from_currency == to_currency:
        return amount

    # Convert from the source currency to the base currency first.
    from_rate = SUPPORTED_CURRENCIES[from_currency]
    amount_in_base = amount / from_rate

    # Then from the base currency to the target currency.
    to_rate = SUPPORTED_CURRENCIES[to_currency]
    return amount_in_base * to_rate


def list_supported_currencies() -> Dict[str, float]:
    """Return a copy of the supported currencies dictionary."""
    return dict(SUPPORTED_CURRENCIES)
