import re
from urllib.parse import parse_qs, urlparse

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


# F4 - Sort
from tests.opencart import BASE_URL

CATEGORY_URL = BASE_URL + "?route=product/category&path=20&limit=100"


def open_category(driver, wait):
    driver.get(CATEGORY_URL)
    wait.until(
        EC.presence_of_element_located((By.ID, "input-sort"))
    )


def select_sort(driver, wait, keyword):
    """Select a sorting option and wait for the page to update."""
    dropdown = Select(
        wait.until(
            EC.element_to_be_clickable((By.ID, "input-sort"))
        )
    )

    options = dropdown.options
    selected = None

    for option in options:
        if keyword in option.get_attribute("value"):
            selected = option
            break

    assert selected is not None, f"Sort option not found: {keyword}"

    expected_value = selected.get_attribute("value")
    previous_select = dropdown._el
    dropdown.select_by_value(expected_value)
    wait.until(EC.staleness_of(previous_select))
    expected_query = parse_qs(urlparse(expected_value).query)
    wait.until(lambda d: parse_qs(urlparse(d.current_url).query) == expected_query)

    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".product-layout")
        )
    )


def get_cards(driver, wait):
    return wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".product-layout")
        )
    )


def get_names(driver, wait):
    cards = get_cards(driver, wait)

    return [
        card.find_element(By.CSS_SELECTOR, "h4 a").text.strip()
        for card in cards
    ]


def get_prices(driver, wait):
    cards = get_cards(driver, wait)
    prices = []

    for card in cards:
        special_price = card.find_elements(
            By.CSS_SELECTOR, ".price-new"
        )

        if special_price:
            price_text = special_price[0].text
        else:
            price_text = card.find_element(
                By.CSS_SELECTOR, ".price"
            ).text

        match = re.search(r"[\d,]+\.\d{2}", price_text)
        assert match, f"Cannot read price: {price_text}"

        prices.append(
            float(match.group().replace(",", ""))
        )

    return prices


def get_models(driver, wait):
    """Read model codes from product detail pages."""
    cards = get_cards(driver, wait)

    urls = [
        card.find_element(
            By.CSS_SELECTOR, "h4 a"
        ).get_attribute("href")
        for card in cards
    ]

    models = []

    for url in urls:
        driver.get(url)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#content")
            )
        )

        details = driver.find_elements(
            By.CSS_SELECTOR, "#content .list-unstyled li"
        )

        model = None

        for detail in details:
            text = detail.text.strip()
            match = re.match(
                r"^(?:Product Code|Model)\s*:\s*(.+)$",
                text,
                re.IGNORECASE,
            )

            if match:
                model = match.group(1).strip()
                break

        assert model, f"Cannot find model for {url}"
        models.append(model)

    return models


# Test Scenario 1: Sort by Name
@pytest.mark.online
def test_sort_by_name(driver, wait):
    open_category(driver, wait)

    select_sort(driver, wait, "sort=pd.name&order=ASC")
    names_asc = get_names(driver, wait)

    assert len(names_asc) > 1
    assert names_asc == sorted(
        names_asc, key=str.casefold
    ), f"Name ascending failed: {names_asc}"

    select_sort(driver, wait, "sort=pd.name&order=DESC")
    names_desc = get_names(driver, wait)

    assert names_desc == sorted(
        names_desc, key=str.casefold, reverse=True
    ), f"Name descending failed: {names_desc}"

    print("PASS: Name ascending and descending")


# Test Scenario 2: Sort by Price
@pytest.mark.online
def test_sort_by_price(driver, wait):
    open_category(driver, wait)

    select_sort(driver, wait, "sort=p.price&order=ASC")
    prices_asc = get_prices(driver, wait)

    assert len(prices_asc) > 1
    assert prices_asc == sorted(
        prices_asc
    ), f"Price ascending failed: {prices_asc}"

    select_sort(driver, wait, "sort=p.price&order=DESC")
    prices_desc = get_prices(driver, wait)

    assert prices_desc == sorted(
        prices_desc, reverse=True
    ), f"Price descending failed: {prices_desc}"

    print("PASS: Price ascending and descending")


# Test Scenario 3: Sort by Model
@pytest.mark.online
def test_sort_by_model(driver, wait):
    open_category(driver, wait)

    select_sort(driver, wait, "sort=p.model&order=ASC")
    models_asc = get_models(driver, wait)

    assert len(models_asc) > 1
    assert models_asc == sorted(
        models_asc, key=str.casefold
    ), f"Model ascending failed: {models_asc}"

    open_category(driver, wait)

    select_sort(driver, wait, "sort=p.model&order=DESC")
    models_desc = get_models(driver, wait)

    assert models_desc == sorted(
        models_desc, key=str.casefold, reverse=True
    ), f"Model descending failed: {models_desc}"

    print("PASS: Model ascending and descending")


