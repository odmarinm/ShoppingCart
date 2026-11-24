"""Shopping use cases. Steps talk to this layer, never to src/pages directly."""
import allure
from playwright.sync_api import Page

from src.enums import CheckoutOption, PaymentMethod
from src.models import AddedProduct, CartSummary, GuestCustomer, HeaderCart, OrderResult
from src.pages import CartPage, CatalogPage, CheckoutPage, OrderSuccessPage, ProductPage


class ShoppingInteractor:
    def __init__(self, page: Page) -> None:
        self.catalog = CatalogPage(page)
        self.product = ProductPage(page)
        self.cart = CartPage(page)
        self.checkout = CheckoutPage(page)
        self.success = OrderSuccessPage(page)

    def open_store(self) -> None:
        self.catalog.open_home()

    def header_cart(self) -> HeaderCart:
        return self.catalog.header_cart()

    def add_product_to_cart(self, name: str, quantity: int = 1) -> AddedProduct:
        """Search the product, open it and add it to the cart."""
        with allure.step(f"Add {quantity} x '{name}' to the cart"):
            self.catalog.search(name)
            self.catalog.open_product(name)
            if quantity != 1:
                self.product.set_quantity(quantity)
            added = AddedProduct(
                name=self.product.name(),
                unit_price=self.product.price(),
                ex_tax_price=self.product.ex_tax_price(),
                quantity=quantity,
                success_message=self.product.add_to_cart(),
            )
        return added

    def view_cart(self) -> CartSummary:
        self.catalog.open_cart_from_header()
        return self.cart.summary()

    def checkout_as_guest(
        self, customer: GuestCustomer, payment: PaymentMethod = PaymentMethod.BANK_TRANSFER
    ) -> OrderResult:
        """From the cart page to the 'Your order has been placed!' page."""
        self.cart.proceed_to_checkout()
        self.checkout.choose_checkout_option(CheckoutOption.GUEST)
        self.checkout.fill_billing_details(customer)
        self.checkout.continue_billing_details()
        shipping_methods = self.checkout.shipping_methods()
        self.checkout.continue_shipping_method()
        self.checkout.choose_payment_method(payment)
        confirmed_order = self.checkout.order_summary()
        self.checkout.confirm_order()
        return OrderResult(
            confirmed_order=confirmed_order,
            shipping_methods=shipping_methods,
            success_url=self.success.url(),
            success_heading=self.success.heading(),
            success_messages=self.success.messages(),
            header_cart_after=self.success.header_cart(),
        )
