"""Prices shown by the store, e.g. '$1,202.00' -> Decimal('1202.00')."""
import re
from decimal import Decimal

_AMOUNT = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def parse_money(text: str) -> Decimal:
    match = _AMOUNT.search(text or "")
    if not match:
        raise ValueError(f"No amount found in {text!r}")
    return Decimal(match.group(0).replace(",", ""))


def format_money(amount: Decimal) -> str:
    return f"${amount:,.2f}"
