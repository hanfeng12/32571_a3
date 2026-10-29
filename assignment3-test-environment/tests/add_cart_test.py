
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# F5 - Add Cart
from tests.opencart import BASE_URL

PRODUCTS = {
    "iMac": 41,
    "iPhone": 40,
}


def open_product(driver, wait, product_name):
    """Open a product detail page."""
    product_id = PRODUCTS[product_name]

    driver.get(
        f"{BASE_URL}?route=product/product&product_id={product_id}"
    )

    wait.until(
        EC.element_to_be_clickable((By.ID, "button-cart"))
    )

    title = driver.find_element(
        By.CSS_SELECTOR, "#content h1"
    ).text.strip()

    assert title == product_name


def add_product(driver, wait, product_name, quantity=1):
    """Add a specified quantity of a product."""
    open_product(driver, wait, product_name)

    quantity_input = driver.find_element(
        By.ID, "input-quantity"
    )

    quantity_input.clear()
    quantity_input.send_keys(str(quantity))

    cart_total = wait.until(
        EC.visibility_of_element_located((By.ID, "cart-total"))
    )
    previous_quantity = int(cart_total.text.split()[0])
    driver.find_element(By.ID, "button-cart").click()

    # Wait for the persistent cart state; the success notification is transient.
    wait.until(
        lambda d: int(d.find_element(By.ID, "cart-total").text.split()[0])
        == previous_quantity + quantity
    )


def open_cart(driver, wait):
    """Open the shopping cart page."""
    driver.get(
        f"{BASE_URL}?route=checkout/cart"
    )

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#content")
        )
    )


def get_cart_items(driver):
    """Read product names and quantities from the cart."""
    rows = driver.find_elements(
        By.CSS_SELECTOR, ".table-responsive tbody tr"
    )

    items = {}

    for row in rows:
        product_links = row.find_elements(
            By.CSS_SELECTOR, "td.text-left a"
        )

        quantity_inputs = row.find_elements(
            By.CSS_SELECTOR, "input[name^='quantity']"
        )

        if not product_links or not quantity_inputs:
            continue

        name = product_links[0].text.strip()
        quantity = int(
            quantity_inputs[0].get_attribute("value")
        )

        items[name] = quantity

    return items


# Test Scenario 1: Add one product
@pytest.mark.online
def test_add_single_product(driver, wait):
    add_product(driver, wait, "iMac", 1)

    open_cart(driver, wait)
    items = get_cart_items(driver)

    assert items == {"iMac": 1}, (
        f"Single product test failed: {items}"
    )

    print("PASS: One iMac added successfully")


# Test Scenario 2: Add multiple quantities
@pytest.mark.online
def test_add_multiple_quantity(driver, wait):
    add_product(driver, wait, "iMac", 3)

    open_cart(driver, wait)
    items = get_cart_items(driver)

    assert items == {"iMac": 3}, (
        f"Multiple quantity test failed: {items}"
    )

    print("PASS: Three iMac units added successfully")


# Test Scenario 3: Add different products
@pytest.mark.online
def test_add_multiple_products(driver, wait):
    add_product(driver, wait, "iMac", 1)
    add_product(driver, wait, "iPhone", 1)

    open_cart(driver, wait)
    items = get_cart_items(driver)

    expected = {
        "iMac": 1,
        "iPhone": 1,
    }

    assert items == expected, (
        f"Multiple products test failed: {items}"
    )

    print("PASS: Both products added successfully")
