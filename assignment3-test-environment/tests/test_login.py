import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.opencart import login, route_is, submit_login

pytestmark = pytest.mark.online


# F2 - User Login
def test_login_valid_credentials(driver, wait, base_url, account):
    login(driver, wait, base_url, account)
    driver.get(base_url + "?route=account/edit")
    email = wait.until(EC.visibility_of_element_located((By.ID, "input-email")))
    assert route_is(driver, "account/edit")
    assert email.get_attribute("value") == account["email"]


def test_login_wrong_password(driver, wait, base_url, account):
    submit_login(driver, wait, base_url, account["email"], "WrongPassword123!")
    alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    assert "No match for E-Mail Address and/or Password" in alert.text
    assert route_is(driver, "account/login")
    driver.get(base_url + "?route=account/account")
    wait.until(lambda d: route_is(d, "account/login"))


def test_login_empty_credentials(driver, wait, base_url):
    submit_login(driver, wait, base_url, "", "")
    alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    assert "No match for E-Mail Address and/or Password" in alert.text
    assert route_is(driver, "account/login")
