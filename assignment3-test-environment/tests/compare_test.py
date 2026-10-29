
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# F6 - Product Compare
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
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#content h1")
        )
    )

    title = driver.find_element(
        By.CSS_SELECTOR, "#content h1"
    ).text.strip()

    assert title == product_name


def add_to_compare(driver, wait, product_name):
    """Add a product to the comparison list."""
    open_product(driver, wait, product_name)

    compare_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[onclick*='compare.add']")
        )
    )

    compare_button.click()

    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".alert-success")
        )
    )


def open_compare(driver, wait):
    """Open the product comparison page."""
    driver.get(
        f"{BASE_URL}?route=product/compare"
    )

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#content table")
        )
    )


def get_compared_products(driver):
    """Read product names, excluding Remove buttons."""
    links = driver.find_elements(
        By.CSS_SELECTOR,
        "#content table tbody tr:first-child td a"
    )

    return [
        link.text.strip()
        for link in links
        if link.text.strip()
        and link.text.strip().lower() != "remove"
    ]


def remove_product(driver, wait, product_name):
    """Remove a product according to its comparison column."""
    products = get_compared_products(driver)

    assert product_name in products, (
        f"Product not found: {product_name}"
    )

    index = products.index(product_name)

    remove_buttons = driver.find_elements(
        By.CSS_SELECTOR,
        "#content table a.btn-danger"
    )

    assert len(remove_buttons) == len(products), (
        f"Unexpected remove button count: "
        f"{len(remove_buttons)}"
    )

    remove_buttons[index].click()

    wait.until(
        lambda d: product_name not in get_compared_products(d)
    )


# Test Scenario 1: Compare a single product
@pytest.mark.online
def test_compare_single_product(driver, wait):
    add_to_compare(driver, wait, "iMac")

    open_compare(driver, wait)
    products = get_compared_products(driver)

    assert products == ["iMac"], (
        f"Single product comparison failed: {products}"
    )

    print("PASS: Single product added to comparison")


# Test Scenario 2: Compare two products
@pytest.mark.online
def test_compare_multiple_products(driver, wait):
    add_to_compare(driver, wait, "iMac")
    add_to_compare(driver, wait, "iPhone")

    open_compare(driver, wait)
    products = get_compared_products(driver)

    assert "iMac" in products
    assert "iPhone" in products
    assert len(products) == 2, (
        f"Unexpected comparison products: {products}"
    )

    print("PASS: Two products compared successfully")


# Test Scenario 3: Remove a compared product
@pytest.mark.online
def test_remove_compared_product(driver, wait):
    add_to_compare(driver, wait, "iMac")
    add_to_compare(driver, wait, "iPhone")

    open_compare(driver, wait)

    products_before = get_compared_products(driver)

    assert "iMac" in products_before
    assert "iPhone" in products_before
    assert len(products_before) == 2

    remove_product(driver, wait, "iMac")

    products_after = get_compared_products(driver)

    assert "iMac" not in products_after
    assert products_after == ["iPhone"], (
        f"Unexpected products after removal: {products_after}"
    )

    print("PASS: Product removed from comparison")
