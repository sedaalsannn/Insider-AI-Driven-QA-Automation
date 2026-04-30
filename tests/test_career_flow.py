import time
from pages.home_page import HomePage
from pages.career_page import CareerPage
from pages.lever_page import LeverPage
from utils.logger import get_logger

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

logger = get_logger(__name__)


def _switch_to_lever_window(driver, main_window, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        if len(driver.window_handles) > 1:
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    logger.info(f"Yeni sekmeye geçildi: {driver.current_url}")
                    return
        if "lever.co" in driver.current_url.lower():
            logger.info(f"Aynı sekmede Lever yüklendi: {driver.current_url}")
            return
        time.sleep(0.5)
    raise TimeoutError(
        f"Lever sayfasına yönlendirilmedi. "
        f"Sekme sayısı: {len(driver.window_handles)}, "
        f"Mevcut URL: {driver.current_url}"
    )


def test_insider_qa_flow(driver: WebDriver):
    home = HomePage(driver)
    career = CareerPage(driver)
    lever = LeverPage(driver)

    # 1. Homepage
    logger.info("STEP 1 — Ana sayfa açılıyor")
    home.open()
    assert home.is_home_page_loaded(), "Homepage load failed"
    home.take_screenshot("01_homepage")

    # 2. Careers
    logger.info("STEP 2 — Careers sayfası açılıyor")
    career.open()

    logger.info("See all teams butonuna tıklanıyor")
    career.click_see_all_teams()

    main_window = driver.current_window_handle

    logger.info("QA Open Positions butonuna tıklanıyor")
    career.click_qa_open_positions()

    # 3. Lever sekmesine geç
    logger.info("Lever sekmesine yönlendirme bekleniyor")
    _switch_to_lever_window(driver, main_window, timeout=15)

    time.sleep(3)
    logger.info(f"Lever sayfasına ulaşıldı: {driver.current_url}")
    assert lever.is_lever_page(), f"Lever sayfasında değiliz: {driver.current_url}"

    # 4. Pozisyon doğrulaması
    lever.wait_for_jobs(timeout=15)
    all_jobs = lever.get_jobs()
    logger.info(f"Toplam {len(all_jobs)} QA pozisyonu bulundu")

    istanbul_jobs = lever.get_istanbul_jobs()
    logger.info(f"Bunlardan {len(istanbul_jobs)} tanesi Istanbul'da")

    assert len(istanbul_jobs) > 0, (
        f"Istanbul'da QA pozisyonu bulunamadı. "
        f"Tüm lokasyonlar: {[j['location'] for j in all_jobs]}"
    )

    # Her Istanbul pozisyonu için Position + Location doğrulaması (case-insensitive)
    for job in istanbul_jobs:
        title = job["title"]
        location = job["location"]

        title_lower = title.lower()
        location_lower = location.lower()

        assert "qa" in title_lower or "quality assurance" in title_lower, (
            f"Pozisyon başlığında QA/Quality Assurance yok: '{title}'"
        )
        assert "istanbul" in location_lower, (
            f"Lokasyon Istanbul içermiyor: '{location}'"
        )
        logger.info(f"  ✓ {title} | {location}")

    lever.take_screenshot("02_jobs_list")

    # 5. Apply butonu
    logger.info("STEP 5 — Apply butonuna tıklanıyor")
    apply_main_window = driver.current_window_handle
    lever.click_apply_first_job()

    end = time.time() + 15
    while time.time() < end:
        if len(driver.window_handles) > 1:
            for handle in driver.window_handles:
                if handle != apply_main_window:
                    driver.switch_to.window(handle)
                    break
            break
        if "/apply" in driver.current_url.lower():
            break
        time.sleep(0.5)

    # 6. Final assertion — detay sayfası doğrulaması
    lever.wait_for_apply_page(timeout=15)

    assert lever.is_lever_apply_page(), f"Lever apply sayfasında değiliz: {driver.current_url}"
    lever.assert_department_is_qa()
    lever.assert_location_is_istanbul()
    lever.assert_apply_button_visible()

    lever.take_screenshot("03_apply_form")
    logger.info(f"✓ Lever apply sayfasına ulaşıldı: {driver.current_url}")
    logger.info(f"  Kategoriler: {lever.get_detail_categories()}")
    logger.info(f"  Lokasyon: {lever.get_detail_location()}")

