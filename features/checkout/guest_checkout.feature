@checkout
@guest_checkout

Feature: Guest checkout
  As a visitor of the OpenCart store
  I want to buy products without creating an account
  So that I can complete a purchase quickly

  Scenario Outline: Buy two products as a guest - <first_product> and <second_product>
    Given I am on the store home page
    When I add <first_quantity> unit(s) of the product "<first_product>" to the cart
    And I add <second_quantity> unit(s) of the product "<second_product>" to the cart
    Then the products have been added to the cart successfully
    When I view the shopping cart
    Then the shopping cart contains the added products
    When I complete the guest checkout as "<first_name> <last_name>" from "<region>, <country>" paying by "<payment>"
    Then the order has been placed successfully

    Examples:
      | first_product            | first_quantity | second_product | second_quantity | first_name | last_name | region         | country        | payment          |
      | MacBook                  | 1              | iPhone         | 1               | Ana        | Lopez     | Bogota D.C.    | Colombia       | Bank Transfer    |
      | Samsung SyncMaster 941BW | 1              | Nikon D300     | 2               | Carlos     | Perez     | Greater London | United Kingdom | Cash On Delivery |
