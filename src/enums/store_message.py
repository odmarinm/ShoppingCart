from enum import StrEnum


class StoreMessage(StrEnum):
    """Texts shown by the store (observed on the real site)."""

    PRODUCT_ADDED = "Success: You have added {product} to your shopping cart!"
    ORDER_PLACED = "Your order has been placed!"
    ORDER_PROCESSED = "Your order has been successfully processed!"
    EMPTY_CART_HEADER = "0 item(s) - $0.00"
