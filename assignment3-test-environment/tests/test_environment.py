"""Environment checks only; these are not the three assessed functional cases."""
from urllib.parse import quote

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.smoke
def test_browser_and_webdriver(driver, wait):
    html = """<!doctype html><title>Assignment 3 Environment Check</title>
    <h1>Selenium environment check</h1>
    <label for='value'>Test input</label><input id='value'>
    <button onclick="document.getElementById('result').textContent =
    document.getElementById('value').value">Verify</button><p id='result'></p>"""
    driver.get("data:text/html;charset=utf-8," + quote(html))
    driver.find_element(By.ID, "value").send_keys("Selenium is ready")
    driver.find_element(By.TAG_NAME, "button").click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "result"), "Selenium is ready"))
    assert driver.title == "Assignment 3 Environment Check"


@pytest.mark.smoke
@pytest.mark.online
def test_assessment_website_accessible(driver, wait, base_url):
    driver.get(base_url + "?route=common/home")
    search = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#search input[name='search']")
    ))
    assert search.is_enabled()
    assert driver.title == "Your Store"
    assert "route=common/home" in driver.current_url
