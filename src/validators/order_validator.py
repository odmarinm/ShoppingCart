"""Order validations. No Playwright here: receives data already read from the pages."""
from src.enums import Route, StoreMessage
from src.models import AddedProduct, CartSummary, OrderResult
from src.utils.checker import Checker
from src.utils.money import format_money
from src.validators.cart_validator import TOTAL, check_sub_total, check_totals


def validate_order_placed(added: list[AddedProduct], cart: CartSummary, order: OrderResult) -> None:
    """The confirmed order contains the cart products and the store confirms the purchase."""
    checker = Checker()
    confirmed = order.confirmed_order

    with checker.group("Validate confirmed order (Step 6: Confirm Order)"):
        checker.equals(
            "products (name x quantity) = cart",
            sorted((line.name, line.quantity) for line in cart.lines),
            sorted((line.name, line.quantity) for line in confirmed.lines),
        )
        for line in confirmed.lines:
            checker.equals(f"{line.name} - total (unit price x quantity)", line.unit_price * line.quantity, line.total)
        check_sub_total(checker, added, confirmed)
        check_totals(checker, confirmed)
        checker.check(
            f"a delivery method is offered: {order.shipping_methods}",
            None if order.shipping_methods else "no delivery method was offered",
        )

    with checker.group("Validate order confirmation page"):
        route = f"route={Route.CHECKOUT_SUCCESS}"
        checker.check(
            f"URL contains '{route}'",
            None if route in order.success_url else f"URL is {order.success_url!r}",
        )
        checker.equals("heading", str(StoreMessage.ORDER_PLACED), order.success_heading)
        checker.check(
            f"message '{StoreMessage.ORDER_PROCESSED}' is shown",
            None if StoreMessage.ORDER_PROCESSED in order.success_messages
            else f"messages shown: {order.success_messages}",
        )
        checker.equals("header cart is empty", str(StoreMessage.EMPTY_CART_HEADER), order.header_cart_after.text)

    cart_total, order_total = cart.totals.get(TOTAL), confirmed.totals.get(TOTAL)
    if cart_total is not None and order_total is not None and cart_total != order_total:
        Checker.info(
            f"Cart total {format_money(cart_total)} differs from the order total {format_money(order_total)}: "
            "taxes and shipping are recalculated with the billing address"
        )

    checker.raise_if_errors("Order")
