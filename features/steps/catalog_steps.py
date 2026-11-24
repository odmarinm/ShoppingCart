from behave import given, then, when

from src.validators.cart_validator import validate_products_added


@given("I am on the store home page")
def step_open_store(context):
    context.shopping.open_store()


@when('I add {quantity:d} unit(s) of the product "{product}" to the cart')
def step_add_product(context, quantity, product):
    context.added_products.append(context.shopping.add_product_to_cart(product, quantity))


@then("the products have been added to the cart successfully")
def step_products_added(context):
    validate_products_added(context.added_products, context.shopping.header_cart())
