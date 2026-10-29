"""F7 Wish List, F8 Review and Rate, F9 Edit Account."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.opencart import BASE_URL, login, route_is

pytestmark = pytest.mark.online


def get_product_url(driver, wait):
    driver.get(BASE_URL + "?route=product/category&path=20")
    return wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".product-thumb h4 a")
    )).get_attribute("href")


def test_add_product_to_wishlist(driver, wait, base_url, account):
    login(driver, wait, base_url, account)
    product_url = get_product_url(driver, wait)
    driver.get(product_url)
    product_name = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#content h1")
    )).text

    def add_to_wishlist():
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[onclick*='wishlist.add']")
        )).click()
        alert = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".alert-success")
        ))
        assert product_name in alert.text
        assert "wish list" in alert.text.lower()

    def wishlist_names():
        driver.get(base_url + "?route=account/wishlist")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#content table")))
        assert route_is(driver, "account/wishlist")
        return [link.text for link in driver.find_elements(
            By.CSS_SELECTOR, "#content table tbody td.text-left a"
        )]

    # Scenario 1: Adding a product returns a success response.
    add_to_wishlist()
    # Scenario 2: The chosen product is present in the saved wish list.
    assert wishlist_names() == [product_name]
    # Scenario 3: Adding it again does not create a duplicate row.
    driver.get(product_url)
    add_to_wishlist()
    assert wishlist_names() == [product_name]


def test_submit_product_review(driver, wait):
    driver.get(get_product_url(driver, wait))
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a[href='#tab-review']")
    )).click()

    def submit_review(text, rating, expected_class):
        name = wait.until(EC.visibility_of_element_located((By.ID, "input-name")))
        name.clear()
        name.send_keys("Automation Test")
        review = driver.find_element(By.ID, "input-review")
        review.clear()
        review.send_keys(text)
        driver.find_element(By.CSS_SELECTOR, f"input[name='rating'][value='{rating}']").click()
        previous_alerts = driver.find_elements(By.CSS_SELECTOR, "#tab-review .alert")
        driver.find_element(By.ID, "button-review").click()
        for previous in previous_alerts:
            wait.until(EC.staleness_of(previous))
        return wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"#tab-review .{expected_class}")
        )).text

    # Scenario 1: A valid review is accepted for moderation.
    assert "Thank you for your review" in submit_review(
        "This is a test review for assignment 3.", 5, "alert-success"
    )
    # Scenario 2: An empty review is rejected by validation.
    assert "Review Text must be between 25 and 1000 characters" in submit_review(
        "", 5, "alert-danger"
    )
    # Scenario 3: A valid review with a different rating is accepted.
    assert "Thank you for your review" in submit_review(
        "A second test review with a different rating.", 4, "alert-success"
    )


def test_edit_account_first_name(driver, wait, base_url, account):
    login(driver, wait, base_url, account)

    def open_edit():
        driver.get(base_url + "?route=account/edit")
        return wait.until(EC.visibility_of_element_located((By.ID, "input-firstname")))

    def save_first_name(field, value):
        field.clear()
        field.send_keys(value)
        driver.find_element(By.CSS_SELECTOR, "#content input[type='submit']").click()

    def assert_saved(value):
        alert = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".alert-success")
        ))
        assert "Your account has been successfully updated" in alert.text
        assert route_is(driver, "account/account")
        field = open_edit()
        assert field.get_attribute("value") == value
        return field

    # Scenario 1: A valid first name is saved and persists after reopening.
    save_first_name(open_edit(), "AutomationTest")
    first_name = assert_saved("AutomationTest")
    # Scenario 2: An empty name is rejected and the saved value is preserved.
    save_first_name(first_name, "")
    error = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#input-firstname + .text-danger")
    ))
    assert "First Name must be between 1 and 32 characters" in error.text
    assert route_is(driver, "account/edit")
    first_name = open_edit()
    assert first_name.get_attribute("value") == "AutomationTest"
    # Scenario 3: Another valid name can replace the previous value.
    save_first_name(first_name, "AutomationTestTwo")
    assert_saved("AutomationTestTwo")
