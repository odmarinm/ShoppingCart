"""Catalog: home page and search results."""
import allure
from playwright.sync_api import expect

from src.enums import Route
from src.pages.base_page import BasePage


class CatalogPage(BasePage):
    @allure.step("Open the store home page")
    def open_home(self) -> None:
        self.go_to(Route.HOME)
        expect(self.page.locator("#logo")).to_be_visible()

    def result_names(self) -> list[str]:
        return [name.strip() for name in self.page.locator(".product-thumb h4 a").all_inner_texts()]

    @allure.step("Open the product '{name}' from the results")
    def open_product(self, name: str) -> None:
        """Click the result whose name is EXACTLY `name` ('MacBook' also returns 'MacBook Air')."""
        link = self.page.locator(".product-thumb h4 a").filter(has_text=name)
        exact = [i for i, text in enumerate(link.all_inner_texts()) if text.strip() == name]
        if not exact:
            raise AssertionError(f"Product '{name}' not found in the results: {self.result_names()}")
        link.nth(exact[0]).click()
        self.page.wait_for_load_state("domcontentloaded")
