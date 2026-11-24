"""Common page behavior: navigation, header (search box and cart button) and alerts.

src/pages is the ONLY layer that talks to Playwright.
"""
import re

import allure
from playwright.sync_api import Locator, Page, expect

from src.config.settings import Settings, get_settings
from src.enums import Route
from src.models import HeaderCart
from src.utils.money import parse_money

_HEADER_CART = re.compile(r"(\d+)\s*item\(s\)\s*-\s*(.+)")


class BasePage:
    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self.page = page
        self.settings = settings or get_settings()

    # ---------- navigation ----------
    def url_for(self, route: Route, **params: str) -> str:
        query = "".join(f"&{key}={value}" for key, value in params.items())
        return f"{self.settings.base_url}/index.php?route={route}{query}"

    def go_to(self, route: Route, **params: str) -> None:
        self.page.goto(self.url_for(route, **params), wait_until="domcontentloaded")

    def wait_for_ajax(self) -> None:
        """Wait until jQuery has no AJAX requests in progress.

        OpenCart stores the session without locking: a request still running can overwrite what
        another one just saved (e.g. the delivery method), so the next action must wait for it.
        """
        self.page.wait_for_function("() => !window.jQuery || window.jQuery.active === 0")

    def heading(self) -> str:
        return self.page.locator("#content h1").first.inner_text().strip()

    # ---------- header ----------
    @property
    def _cart_button(self) -> Locator:
        return self.page.locator("#cart-total")

    def header_cart(self) -> HeaderCart:
        text = self._cart_button.inner_text().strip()
        match = _HEADER_CART.search(text)
        if not match:
            raise AssertionError(f"Unexpected header cart text: {text!r}")
        return HeaderCart(text=text, items=int(match.group(1)), amount=parse_money(match.group(2)))

    def wait_header_cart_change(self, previous_text: str) -> None:
        """The header cart is refreshed by JavaScript shortly after a product is added."""
        expect(self._cart_button).not_to_have_text(previous_text)

    @allure.step("Search the catalog for '{term}'")
    def search(self, term: str) -> None:
        self.page.locator("#search input[name='search']").fill(term)
        self.page.locator("#search button").click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Open the shopping cart from the header")
    def open_cart_from_header(self) -> None:
        self.page.locator("#top-links a[title='Shopping Cart']").click()
        self.page.wait_for_load_state("domcontentloaded")

    # ---------- alerts ----------
    def success_alert(self) -> str:
        alert = self.page.locator(".alert-success").first
        expect(alert).to_be_visible()
        return self._clean_alert(alert.inner_text())

    def danger_alerts(self) -> list[str]:
        alerts = self.page.locator(".alert-danger:visible")
        return [self._clean_alert(text) for text in alerts.all_inner_texts()]

    @staticmethod
    def _clean_alert(text: str) -> str:
        """Remove the close button ('×') and extra spaces."""
        return " ".join(text.replace("×", " ").split())
