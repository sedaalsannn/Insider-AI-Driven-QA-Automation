"""
Pytest fixtures ve test execution hook'lari.

- driver fixture: Headless/headful Chrome WebDriver
- pytest_runtest_makereport hook: Test fail olursa otomatik screenshot alır,
  hem pytest-html raporuna hem de Allure'a ekler.
"""

import os
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


@pytest.fixture
def driver(request):
    """Selenium Chrome driver fixture.

    HEADLESS=true env var ile headless modda calisir (CI'da default).
    Selenium 4.6+ Selenium Manager kullanir, ayrica driver indirme gerekmez.
    """
    headless = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")

    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(60)

    # Hook'tan erisilebilmesi icin driver'i item'a iliştir
    request.node._driver = drv
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    """Test fail oldugunda otomatik screenshot alır ve raporlara ekler."""
    outcome = yield
    report = outcome.get_result()

    # Sadece test calistirma fazinda ve fail olduysa screenshot al
    if report.when != "call" or not report.failed:
        return

    drv = getattr(item, "_driver", None)
    if drv is None:
        return

    os.makedirs("reports/screenshots", exist_ok=True)
    screenshot_path = f"reports/screenshots/FAIL_{item.name}.png"

    try:
        drv.save_screenshot(screenshot_path)
        print(f"\n[FAIL SCREENSHOT] {screenshot_path}")

        # pytest-html raporuna gomme (yeni ve eski API desteği)
        try:
            from pytest_html import extras
            # pytest-html 4.x: report.extras, eski: report.extra
            extra = getattr(report, "extras", None)
            if extra is None:
                extra = getattr(report, "extra", [])
            extra.append(extras.image(screenshot_path))
            if hasattr(report, "extras"):
                report.extras = extra
            else:
                report.extra = extra
        except Exception as e:
            print(f"pytest-html'e screenshot eklenemedi: {e}")

        # Allure raporuna attach
        try:
            with open(screenshot_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"FAIL_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception as e:
            print(f"Allure'a screenshot eklenemedi: {e}")

    except Exception as e:
        print(f"Screenshot alinamadi: {e}")


def pytest_html_report_title(report):
    """pytest-html raporu icin baslik."""
    report.title = "Insider QA Automation - Test Report"
