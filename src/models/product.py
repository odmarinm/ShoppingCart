from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class AddedProduct:
    """A product added to the cart, as seen on its product page."""

    name: str
    unit_price: Decimal  # price shown on the product page (taxes of the store's default address included)
    ex_tax_price: Decimal  # 'Ex Tax' price shown on the product page
    quantity: int
    success_message: str
