import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.opencart import (
    fill_registration, new_account, register, route_is, submit_registration,
)

pytestmark = pytest.mark.online


# F1 - User Registration
def test_registration_valid_details(driver, wait, base_url):
    register(driver, wait, base_url, new_account())
    driver.get(base_url + "?route=account/edit")
    wait.until(lambda d: route_is(d, "account/edit"))
    assert wait.until(EC.visibility_of_element_located(
        (By.ID, "input-firstname")
    )).get_attribute("value") == "Automation"


def test_registration_duplicate_email(driver, wait, base_url, account):
    fill_registration(driver, wait, base_url, account)
    submit_registration(driver)
    alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    assert "E-Mail Address is already registered" in alert.text
    assert route_is(driver, "account/register")


def test_registration_password_mismatch(driver, wait, base_url):
    fill_registration(driver, wait, base_url, new_account(), confirm="DifferentPassword123!")
    submit_registration(driver)
    error = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#input-confirm + .text-danger")
    ))
    assert "Password confirmation does not match password" in error.text
    assert route_is(driver, "account/register")
