from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.opencart import route_is

pytestmark = pytest.mark.online


def search(driver, wait, base_url, keyword):
    driver.get(base_url + "?route=common/home")
    field = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#search input[name='search']")
    ))
    field.clear()
    field.send_keys(keyword)
    driver.find_element(By.CSS_SELECTOR, "#search button").click()
    wait.until(lambda d: route_is(d, "product/search"))
    wait.until(EC.visibility_of_element_located((By.ID, "input-search")))
    assert parse_qs(urlparse(driver.current_url).query).get("search") == [keyword]
    return [e.text.strip() for e in driver.find_elements(
        By.CSS_SELECTOR, "#content .product-thumb h4 a"
    )]


# F3 - Product Search
def test_search_exact_product(driver, wait, base_url):
    names = search(driver, wait, base_url, "iPhone")
    assert names == ["iPhone"], f"Unexpected search results: {names}"


def test_search_partial_product_name(driver, wait, base_url):
    names = search(driver, wait, base_url, "MacBook")
    assert set(names) == {"MacBook", "MacBook Air", "MacBook Pro"}
    assert len(names) == 3


def test_search_no_matching_product(driver, wait, base_url):
    names = search(driver, wait, base_url, "a3-no-product-" + uuid4().hex)
    assert names == []
    assert "There is no product that matches the search criteria." in driver.find_element(
        By.ID, "content"
    ).text
