"""Cart validations. No Playwright here: receives data already read from the pages."""
from decimal import Decimal

from src.enums import StoreMessage
from src.models import AddedProduct, CartSummary, HeaderCart
from src.utils.checker import Checker
from src.utils.money import format_money

TOTAL = "Total"
SUB_TOTAL = "Sub-Total"


def expected_items(added: list[AddedProduct]) -> int:
    return sum(product.quantity for product in added)


def expected_amount(added: list[AddedProduct]) -> Decimal:
    return sum((product.unit_price * product.quantity for product in added), Decimal("0"))


def expected_sub_total(added: list[AddedProduct]) -> Decimal:
    """Sub-Total is always WITHOUT taxes: sum of the 'Ex Tax' prices x quantity."""
    return sum((product.ex_tax_price * product.quantity for product in added), Decimal("0"))


def check_sub_total(checker: Checker, added: list[AddedProduct], summary: CartSummary) -> None:
    checker.equals(
        f"{SUB_TOTAL} (= sum of 'Ex Tax' prices x quantity)",
        expected_sub_total(added),
        summary.totals.get(SUB_TOTAL),
    )


def validate_products_added(added: list[AddedProduct], header: HeaderCart) -> None:
    """Every product showed its success message and the header cart counts all of them."""
    checker = Checker()
    with checker.group("Validate 'Add to Cart' success messages"):
        for product in added:
            checker.equals(
                f"message for '{product.name}'",
                StoreMessage.PRODUCT_ADDED.format(product=product.name),
                product.success_message,
            )
    _check_header(checker, "Validate header cart", added, header)
    checker.raise_if_errors("Adding the products to the cart")


def validate_cart(added: list[AddedProduct], cart: CartSummary, header: HeaderCart) -> None:
    """The cart shows exactly the added products, with the product page prices and correct totals."""
    checker = Checker()

    with checker.group("Validate cart products"):
        checker.equals("number of products", len(added), len(cart.lines))
        for product in added:
            line = cart.line(product.name)
            if line is None:
                checker.check(f"'{product.name}' is in the cart", f"'{product.name}' is not in the cart")
                continue
            checker.equals(f"{product.name} - quantity", product.quantity, line.quantity)
            checker.equals(f"{product.name} - unit price (= product page)", product.unit_price, line.unit_price)
            checker.equals(f"{product.name} - total (unit price x quantity)", line.unit_price * line.quantity, line.total)

    with checker.group("Validate cart totals"):
        check_sub_total(checker, added, cart)
        check_totals(checker, cart)
        lines_sum = sum((line.total for line in cart.lines), Decimal("0"))
        checker.equals(f"{TOTAL} (= sum of product totals)", lines_sum, cart.totals.get(TOTAL))

    _check_header(checker, "Validate header cart matches the cart", added, header, cart.totals.get(TOTAL))

    for warning in cart.warnings:
        Checker.info(f"Warning shown by the store: {warning}")

    checker.raise_if_errors("Shopping cart")


def check_totals(checker: Checker, summary: CartSummary) -> None:
    """Sub-Total, taxes and shipping must add up to the Total."""
    if TOTAL not in summary.totals:
        checker.check(f"'{TOTAL}' row is shown", f"'{TOTAL}' row not found in {list(summary.totals)}")
        return
    parts = {label: amount for label, amount in summary.totals.items() if label != TOTAL}
    detail = " + ".join(f"{label} {format_money(amount)}" for label, amount in parts.items())
    checker.equals(f"{TOTAL} (= {detail})", sum(parts.values(), Decimal("0")), summary.totals[TOTAL])


def _check_header(
    checker: Checker,
    title: str,
    added: list[AddedProduct],
    header: HeaderCart,
    amount: Decimal | None = None,
) -> None:
    with checker.group(f"{title}: '{header.text}'"):
        checker.equals("items", expected_items(added), header.items)
        checker.equals("amount", amount if amount is not None else expected_amount(added), header.amount)
