from behave import then, when

from src.validators.cart_validator import validate_cart


@when("I view the shopping cart")
def step_view_cart(context):
    context.cart = context.shopping.view_cart()


@then("the shopping cart contains the added products")
def step_cart_contains_products(context):
    validate_cart(context.added_products, context.cart, context.shopping.header_cart())
