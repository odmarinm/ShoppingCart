import re
from decimal import Decimal

import allure
from playwright.sync_api import Locator, expect

from src.enums import Route
from src.models import CartLine, CartSummary
from src.pages.base_page import BasePage
from src.utils.money import parse_money


class CartPage(BasePage):
    @property
    def _product_rows(self) -> Locator:
        return self.page.locator("#content form table tbody tr")

    @property
    def _total_rows(self) -> Locator:
        return self.page.locator("#content .col-sm-offset-8 table tr")

    def wait_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(re.escape(f"route={Route.CART}")))
        expect(self._product_rows.first).to_be_visible()

    def summary(self) -> CartSummary:
        self.wait_loaded()
        return CartSummary(lines=self._lines(), totals=self._totals(), warnings=self.danger_alerts())

    def _lines(self) -> list[CartLine]:
        lines = []
        for row in self._product_rows.all():
            cells = row.locator("td")
            lines.append(
                CartLine(
                    name=cells.nth(1).locator("a").first.inner_text().strip(),
                    model=cells.nth(2).inner_text().strip(),
                    quantity=int(cells.nth(3).locator("input").input_value()),
                    unit_price=parse_money(cells.nth(4).inner_text()),
                    total=parse_money(cells.nth(5).inner_text()),
                )
            )
        return lines

    def _totals(self) -> dict[str, Decimal]:
        totals = {}
        for row in self._total_rows.all():
            cells = row.locator("td")
            label = cells.nth(0).inner_text().strip().rstrip(":")
            totals[label] = parse_money(cells.nth(1).inner_text())
        return totals

    @allure.step("Click 'Checkout'")
    def proceed_to_checkout(self) -> None:
        self.page.locator("#content .buttons a", has_text="Checkout").click()
        self.page.wait_for_load_state("domcontentloaded")
