from decimal import Decimal

import allure

from src.pages.base_page import BasePage
from src.utils.money import parse_money


class ProductPage(BasePage):
    def name(self) -> str:
        return self.heading()

    def price(self) -> Decimal:
        """Price shown on the product page (with taxes, as in the cart)."""
        return parse_money(self.page.locator("#content ul.list-unstyled h2").first.inner_text())

    def ex_tax_price(self) -> Decimal:
        """'Ex Tax: $500.00' line below the price."""
        return parse_money(self.page.locator("#content ul.list-unstyled li", has_text="Ex Tax:").first.inner_text())

    @allure.step("Set quantity to {quantity}")
    def set_quantity(self, quantity: int) -> None:
        """Changing the quantity fires an AJAX call (getRecurringDescription) whose response removes
        every alert of the page. Leave the field and let it finish, or it may erase the
        'Add to Cart' success message."""
        quantity_input = self.page.locator("#input-quantity")
        quantity_input.fill(str(quantity))
        quantity_input.press("Tab")
        self.wait_for_ajax()

    @allure.step("Click 'Add to Cart'")
    def add_to_cart(self) -> str:
        """Add the product and return the success message once the header cart is refreshed."""
        previous = self.header_cart().text
        self.wait_for_ajax()
        self.page.locator("#button-cart").click()
        message = self.success_alert()
        self.wait_header_cart_change(previous)
        return message
