from enum import StrEnum


class Route(StrEnum):
    """OpenCart routes, used as index.php?route=<value>."""

    HOME = "common/home"
    SEARCH = "product/search"
    CART = "checkout/cart"
    CHECKOUT = "checkout/checkout"
    CHECKOUT_SUCCESS = "checkout/success"
