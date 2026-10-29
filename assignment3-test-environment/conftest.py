"""Shared Selenium fixtures. Each test gets an isolated temporary browser profile."""
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from tests.opencart import BASE_URL, new_account, register, logout

ROOT = Path(__file__).resolve().parent


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Show the test browser")


def pytest_configure(config):
    (ROOT / "reports" / "screenshots").mkdir(parents=True, exist_ok=True)
    # Project-local downloads; do not use the user's old Chrome or browser profile.
    os.environ["SE_CACHE_PATH"] = str(ROOT / ".cache" / "selenium")
    os.environ["SE_AVOID_STATS"] = "true"
    os.environ["SE_FORCE_BROWSER_DOWNLOAD"] = "true"
    os.environ["SE_SKIP_BROWSER_IN_PATH"] = "true"
    os.environ["SE_SKIP_DRIVER_IN_PATH"] = "true"


@pytest.fixture
def driver(request):
    options = Options()
    options.browser_version = (ROOT / "browser-version.txt").read_text().strip()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    log_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    service = Service(log_output=str(ROOT / "reports" / f"{log_name}.driver.log"),
                      service_args=["--verbose"])
    browser = webdriver.Chrome(options=options, service=service)
    try:
        browser.set_page_load_timeout(60)
        browser.set_script_timeout(30)
        caps = browser.capabilities
        try:
            git_version = subprocess.check_output(
                ["git", "--version"], text=True, timeout=5
            ).strip()
        except (OSError, subprocess.SubprocessError):
            git_version = "not available"
        environment = {
            "recorded_at": datetime.now().astimezone().isoformat(),
            "os": platform.system(),
            "os_version": platform.mac_ver()[0] if sys.platform == "darwin" else platform.version(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "selenium": version("selenium"),
            "pytest": version("pytest"),
            "pytest_html": version("pytest-html"),
            "browser": "Chrome for Testing",
            "browser_version": caps.get("browserVersion"),
            "chromedriver_version": caps.get("chrome", {}).get("chromedriverVersion", "").split(" ")[0],
            "headless": not request.config.getoption("--headed"),
            "viewport_requested": "1440x1000",
            "git": git_version,
            "target_url": BASE_URL + "?route=common/home",
        }
        (ROOT / "reports" / "environment.json").write_text(
            json.dumps(environment, indent=2), encoding="utf-8"
        )
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 20)


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def account(driver, wait, base_url):
    credentials = new_account()
    register(driver, wait, base_url, credentials)
    logout(driver, wait, base_url)
    return credentials


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    browser = item.funcargs.get("driver")
    if browser is None or not (report.when == "call" or (report.when == "setup" and report.failed)):
        return
    try:
        screenshot = browser.get_screenshot_as_base64()
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
        browser.save_screenshot(str(ROOT / "reports" / "screenshots" / f"{name}.png"))
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(screenshot, name="Browser screenshot"))
        report.extras = extras
    except Exception as exc:
        # Screenshot failure must not hide the original test result.
        report.sections.append(("Screenshot capture error", str(exc)))
