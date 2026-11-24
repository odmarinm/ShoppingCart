"""Checkout: a single page with 6 accordion steps loaded by AJAX."""
from decimal import Decimal

import allure
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, expect

from src.enums import CheckoutOption, PaymentMethod
from src.models import CartLine, CartSummary, GuestCustomer
from src.pages.base_page import BasePage
from src.utils.money import parse_money

PAYMENT_ADDRESS = "#collapse-payment-address"
SHIPPING_METHOD = "#collapse-shipping-method"
PAYMENT_METHOD = "#collapse-payment-method"
CONFIRM = "#collapse-checkout-confirm"


class CheckoutPage(BasePage):
    # ---------- Step 1: Checkout Options ----------
    @allure.step("Step 1 - Select '{option}' and continue")
    def choose_checkout_option(self, option: CheckoutOption) -> None:
        self.page.locator(f"input[name='account'][value='{option}']").check()
        self._continue("#button-account", next_button="#button-guest", panel=PAYMENT_ADDRESS)

    # ---------- Step 2: Billing Details ----------
    def fill_billing_details(self, customer: GuestCustomer) -> None:
        with allure.step(f"Step 2 - Fill in the billing details of {customer.first_name} {customer.last_name}"):
            self._fill_billing_details(customer)

    def _fill_billing_details(self, customer: GuestCustomer) -> None:
        fields = {
            "#input-payment-firstname": customer.first_name,
            "#input-payment-lastname": customer.last_name,
            "#input-payment-email": customer.email,
            "#input-payment-telephone": customer.telephone,
            "#input-payment-address-1": customer.address_1,
            "#input-payment-city": customer.city,
            "#input-payment-postcode": customer.post_code,
        }
        for selector, value in fields.items():
            self.page.locator(selector).fill(value)
        # The region list is reloaded by AJAX when the form opens (default country) and after
        # choosing the country: every reload resets the selected region, so wait for all of them.
        self.wait_for_ajax()
        self.page.locator("#input-payment-country").select_option(label=customer.country)
        self.wait_for_ajax()
        zone = self.page.locator("#input-payment-zone")
        expect(zone.locator("option", has_text=customer.region).first).to_be_attached()
        zone.select_option(label=customer.region)
        expect(zone.locator("option:checked")).to_have_text(customer.region)

    @allure.step("Step 2 - Continue (delivery address = billing address)")
    def continue_billing_details(self) -> None:
        self._continue("#button-guest", next_button="#button-shipping-method", panel=PAYMENT_ADDRESS)

    # ---------- Step 4: Delivery Method ----------
    def shipping_methods(self) -> list[str]:
        labels = self.page.locator(f"{SHIPPING_METHOD} .radio label").all_inner_texts()
        return [" ".join(label.split()) for label in labels]

    @allure.step("Step 4 - Keep the default delivery method and continue")
    def continue_shipping_method(self) -> None:
        self._continue("#button-shipping-method", next_button="#button-payment-method", panel=SHIPPING_METHOD)

    # ---------- Step 5: Payment Method ----------
    def choose_payment_method(self, method: PaymentMethod) -> None:
        with allure.step(f"Step 5 - Pay with '{method.label}', accept the Terms & Conditions and continue"):
            self.page.locator(f"input[name='payment_method'][value='{method}']").check()
            self.page.locator(f"{PAYMENT_METHOD} input[name='agree']").check()
            self._continue("#button-payment-method", next_button="#button-confirm", panel=PAYMENT_METHOD)

    # ---------- Step 6: Confirm Order ----------
    def order_summary(self) -> CartSummary:
        table = self.page.locator(f"{CONFIRM} table")
        lines = []
        for row in table.locator("tbody tr").all():
            cells = row.locator("td")
            lines.append(
                CartLine(
                    name=cells.nth(0).locator("a").first.inner_text().strip(),
                    model=cells.nth(1).inner_text().strip(),
                    quantity=int(cells.nth(2).inner_text().strip()),
                    unit_price=parse_money(cells.nth(3).inner_text()),
                    total=parse_money(cells.nth(4).inner_text()),
                )
            )
        totals: dict[str, Decimal] = {}
        for row in table.locator("tfoot tr").all():
            cells = row.locator("td")
            totals[cells.nth(0).inner_text().strip().rstrip(":")] = parse_money(cells.nth(1).inner_text())
        return CartSummary(lines=lines, totals=totals)

    @allure.step("Step 6 - Click 'Confirm Order'")
    def confirm_order(self) -> None:
        self.wait_for_ajax()
        self.page.locator("#button-confirm").click()
        self.page.wait_for_url("**route=checkout/success**")

    # ---------- helpers ----------
    def _continue(self, button: str, next_button: str, panel: str) -> None:
        """Click 'Continue' and wait for the next step. If it does not open, report why.

        Before clicking, wait for the AJAX requests of the current step to finish: OpenCart saves the
        session without locking, and a request still running can erase what this step saves.
        """
        self.wait_for_ajax()
        self.page.locator(button).click()
        try:
            expect(self.page.locator(next_button)).to_be_visible()
        except (AssertionError, PlaywrightError) as exc:
            errors = self._errors(self.page.locator(panel))
            if self.page.locator("#button-account").is_visible():
                errors.append("the store sent the checkout back to Step 1 (the session lost the previous steps)")
            detail = "; ".join(errors) if errors else "no error message shown"
            raise AssertionError(f"Next checkout step did not open after '{button}': {detail}") from exc
        self.wait_for_ajax()

    def _errors(self, panel: Locator) -> list[str]:
        texts = panel.locator(".text-danger:visible").all_inner_texts() + self.danger_alerts()
        return [" ".join(text.split()) for text in texts if text.strip()]
