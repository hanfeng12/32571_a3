from secrets import token_hex
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://opencart.abstracta.us/index.php"


def route_is(driver, route):
    return parse_qs(urlparse(driver.current_url).query).get("route") == [route]


def new_account():
    return {
        "firstname": "Automation",
        "lastname": "Student",
        "email": f"a3-{uuid4().hex}@example.com",
        "telephone": "0400000000",
        "password": "A3!" + token_hex(10),
    }


def fill_registration(driver, wait, base_url, account, confirm=None):
    driver.get(base_url + "?route=account/register")
    wait.until(EC.visibility_of_element_located((By.ID, "input-firstname")))
    for name, value in account.items():
        field = driver.find_element(By.ID, "input-" + name)
        field.clear()
        field.send_keys(value)
    driver.find_element(By.ID, "input-confirm").send_keys(
        account["password"] if confirm is None else confirm
    )
    driver.find_element(By.CSS_SELECTOR, "input[name='agree']").click()


def submit_registration(driver):
    driver.find_element(By.CSS_SELECTOR, "#content input[type='submit']").click()


def register(driver, wait, base_url, account):
    fill_registration(driver, wait, base_url, account)
    submit_registration(driver)
    wait.until(lambda d: route_is(d, "account/success"))
    content = wait.until(EC.visibility_of_element_located((By.ID, "content")))
    assert "Your new account has been successfully created!" in content.text


def logout(driver, wait, base_url):
    driver.get(base_url + "?route=account/logout")
    wait.until(lambda d: route_is(d, "account/logout"))
    content = wait.until(EC.visibility_of_element_located((By.ID, "content")))
    assert "You have been logged off your account." in content.text


def submit_login(driver, wait, base_url, email, password):
    driver.get(base_url + "?route=account/login")
    wait.until(EC.visibility_of_element_located((By.ID, "input-email"))).send_keys(email)
    driver.find_element(By.ID, "input-password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#content input[type='submit']").click()


def login(driver, wait, base_url, account):
    submit_login(driver, wait, base_url, account["email"], account["password"])
    wait.until(lambda d: route_is(d, "account/account"))
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#content a[href*='route=account/edit']")
    ))
