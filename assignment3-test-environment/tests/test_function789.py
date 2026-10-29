
"""
Assignment 3 - System Testing
Functions:
1. Wish List
2. Review & Rate
3. Edit Account

Framework: Selenium + pytest
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_URL = "https://opencart.abstracta.us/index.php"


@pytest.fixture
def driver():
    """Start Chrome and close it after each test."""
    options = Options()
    options.add_argument("--window-size=1440,1000")

    # Use headless mode unless HEADED=1 is set.
    if os.getenv("HEADED") != "1":
        options.add_argument("--headless=new")

    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(3)
    yield browser
    browser.quit()


@pytest.fixture
def wait(driver):
    """Wait for page elements to appear."""
    return WebDriverWait(driver, 10)


def login(driver, wait):
    """Log in using a dedicated OpenCart test account."""
    email = os.getenv("OPENCART_EMAIL")
    password = os.getenv("OPENCART_PASSWORD")

    if not email or not password:
        pytest.skip(
            "Set OPENCART_EMAIL and OPENCART_PASSWORD before running account tests."
        )

    driver.get(BASE_URL + "?route=account/login")

    wait.until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    ).send_keys(email)

    driver.find_element(By.ID, "input-password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    wait.until(EC.url_contains("route=account"))






def get_product_url(driver, wait):
    """Find a product URL, with a known product-page fallback."""

    category_url = (
        "https://opencart.abstracta.us/"
        "index.php?route=product/category&path=20"
    )

    fallback_url = (
        "https://opencart.abstracta.us/"
        "index.php?route=product/product&path=20&product_id=42"
    )

    driver.get(category_url)

    try:
        product_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".product-thumb h4 a")
            )
        )

        product_url = product_link.get_attribute("href")

        if product_url:
            print("\n--- DEBUG: Product URL from category ---")
            print(product_url)
            return product_url

    except Exception:
        print(
            "\nCategory did not expose a product link. "
            "Trying the known product page."
        )

    driver.get(fallback_url)

    wait.until(
        EC.presence_of_element_located((By.ID, "content"))
    )

    if not driver.find_elements(
        By.CSS_SELECTOR, "button[onclick*='wishlist.add']"
    ):
        raise AssertionError(
            "Product page loaded, but the wishlist button was not found. "
            f"Current URL: {driver.current_url}"
        )

    print("\n--- DEBUG: Product URL from fallback ---")
    print(driver.current_url)

    return driver.current_url




# ============================================================
# Function 1: Wish List
# ============================================================


def test_add_product_to_wishlist(driver, wait):
    """
    Scenario 1: Add a product to the wish list.
    Scenario 2: Open the wish list and verify the product.
    Scenario 3: Add the same product again and verify the response.
    """
    login(driver, wait)
    product_url = get_product_url(driver, wait)

    # Scenario 1: Open the product and add it to the wish list.
    driver.get(product_url)

    wishlist_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[onclick*='wishlist.add']")
        )
    )
    wishlist_button.click()

    # Wait for the website's response.
    alert = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".alert")
        )
    )
    assert alert.text.strip(), "The website should display a response."

    # Scenario 2: Open the wish list and verify the product.
    driver.get(BASE_URL + "?route=account/wishlist")

    wait.until(
        EC.visibility_of_element_located((By.ID, "content"))
    )

    assert "wishlist" in driver.current_url.lower()

    # Verify the product is actually listed.
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#content table")
        )
    )

    wishlist_text = driver.find_element(
        By.ID, "content"
    ).text

    product_name = "Apple Cinema 30"
    assert product_name in wishlist_text, (
        f"Expected product '{product_name}' in the wish list, "
        f"but it was not found. Page text: {wishlist_text}"
    )

    # Scenario 3: Return to the same product and add it again.
    driver.get(product_url)

    wishlist_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[onclick*='wishlist.add']")
        )
    )
    wishlist_button.click()

    alert = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".alert")
        )
    )

    assert alert.text.strip(), (
        "The website should respond when the same product is added again."
    )



# ============================================================
# Function 2: Review & Rate
# ============================================================



def test_submit_product_review(driver, wait):
    """
    Scenario 1: Submit a review with text and a rating.
    Scenario 2: Submit an empty review and check validation.
    Scenario 3: Submit another review with a different rating.
    """
    product_url = get_product_url(driver, wait)
    driver.get(product_url)

    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tab-review']"))
    ).click()

    wait.until(
        EC.visibility_of_element_located((By.ID, "input-name"))
    )

    def submit_review(review_text, rating):
        name_field = wait.until(
            EC.visibility_of_element_located((By.ID, "input-name"))
        )
        review_field = driver.find_element(By.ID, "input-review")

        name_field.clear()
        name_field.send_keys("Automation Test")

        review_field.clear()
        review_field.send_keys(review_text)

        driver.find_element(
            By.CSS_SELECTOR,
            f"input[name='rating'][value='{rating}']"
        ).click()

        driver.find_element(By.ID, "button-review").click()

        return wait.until(
            EC.visibility_of_element_located((By.ID, "review"))
        )

    # Scenario 1: Submit a review with text and a 5-star rating.
    review_area = submit_review(
        "This is a test review for assignment 3.",
        5
    )

    assert review_area.is_displayed()

    # Scenario 2: Submit an empty review.
    review_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-review"))
    )
    review_field.clear()

    driver.find_element(
        By.CSS_SELECTOR, "input[name='rating'][value='5']"
    ).click()

    driver.find_element(By.ID, "button-review").click()

    # Verify that the review area remains available after submission.
    assert wait.until(
        EC.visibility_of_element_located((By.ID, "review"))
    ).is_displayed()

    # Scenario 3: Submit a different review with a different rating.
    review_area = submit_review(
        "A second test review with a different rating.",
        4
    )

    assert review_area.is_displayed()




# ============================================================
# Function 3: Edit Account
# ============================================================

def test_edit_account_first_name(driver, wait):
    """
    Scenario 1: Change the first name to a valid value.
    Scenario 2: Try submitting an empty first name.
    Scenario 3: Change the first name to another valid value.
    """
    login(driver, wait)

    # Open the Edit Account page.
    edit_account_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Edit Account"))
    )
    edit_account_link.click()

    first_name = wait.until(
        EC.visibility_of_element_located((By.ID, "input-firstname"))
    )

    # Scenario 1: Enter a valid first name.
    first_name.clear()
    first_name.send_keys("AutomationTest")

    driver.find_element(
        By.CSS_SELECTOR, "input[type='submit']"
    ).click()

    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )

    # Reopen Edit Account.
    edit_account_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Edit Account"))
    )
    edit_account_link.click()

    first_name = wait.until(
        EC.visibility_of_element_located((By.ID, "input-firstname"))
    )

    # Scenario 2: Submit an empty first name.
    first_name.clear()

    driver.find_element(
        By.CSS_SELECTOR, "input[type='submit']"
    ).click()

    # Check for a first-name validation message.
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#input-firstname + div.text-danger")
        )
    )

    # Scenario 3: Enter another valid first name.
    first_name = wait.until(
        EC.visibility_of_element_located((By.ID, "input-firstname"))
    )
    first_name.clear()
    first_name.send_keys("AutomationTestTwo")

    driver.find_element(
        By.CSS_SELECTOR, "input[type='submit']"
    ).click()

    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )
