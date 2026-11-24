"""Reusable assertions with readable messages in the report."""
from decimal import Decimal
from typing import Any

from src.utils.money import format_money


def show(value: Any) -> str:
    """Display a value in messages/report (amounts as '$1,202.00')."""
    if isinstance(value, Decimal):
        return format_money(value)
    return repr(value)


def assert_equals(actual: Any, expected: Any, field: str = "value") -> None:
    """Raise AssertionError if actual != expected, showing the field and both values."""
    assert actual == expected, f"{field}: expected {show(expected)}, got {show(actual)}"
