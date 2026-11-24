from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class CartLine:
    """One product row of the cart table (also used for the order confirmation table)."""

    name: str
    model: str
    quantity: int
    unit_price: Decimal
    total: Decimal


@dataclass(frozen=True)
class CartSummary:
    """Product rows and totals ('Sub-Total', taxes, 'Total') of a cart or an order."""

    lines: list[CartLine]
    totals: dict[str, Decimal] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def line(self, name: str) -> CartLine | None:
        return next((line for line in self.lines if line.name == name), None)


@dataclass(frozen=True)
class HeaderCart:
    """The black cart button of the header, e.g. '2 item(s) - $725.20'."""

    text: str
    items: int
    amount: Decimal
