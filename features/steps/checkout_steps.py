from behave import then, when

from src.builders.guest_customer_builder import GuestCustomerBuilder
from src.enums import PaymentMethod
from src.validators.order_validator import validate_order_placed


@when(
    'I complete the guest checkout as "{first_name} {last_name}" '
    'from "{region}, {country}" paying by "{payment}"'
)
def step_guest_checkout(context, first_name, last_name, region, country, payment):
    context.customer = (
        GuestCustomerBuilder()
        .with_names(first_name, last_name)
        .with_location(country, region)
        .build()
    )
    context.order = context.shopping.checkout_as_guest(context.customer, PaymentMethod.from_label(payment))


@then("the order has been placed successfully")
def step_order_placed(context):
    validate_order_placed(context.added_products, context.cart, context.order)
