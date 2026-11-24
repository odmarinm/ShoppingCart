from dataclasses import dataclass

from src.models.cart import CartSummary, HeaderCart


@dataclass(frozen=True)
class OrderResult:
    """What the guest checkout produced: the confirmed order (Step 6) and the success page."""

    confirmed_order: CartSummary
    shipping_methods: list[str]
    success_url: str
    success_heading: str
    success_messages: list[str]
    header_cart_after: HeaderCart
