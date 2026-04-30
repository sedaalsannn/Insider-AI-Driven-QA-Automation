import allure
from selenium.webdriver.common.by import By
from base.base_page import BasePage


class HomePage(BasePage):
    URL = "https://insiderone.com/"

    # Ana bloklar
    HEADER_MENU = (By.XPATH, "//div[@class='header-menu']")
    COMPANY_LOGO = (By.XPATH, "//div[@class='header-logo']")
    HERO_SECTION = (By.XPATH, "//section[@class='homepage-hero']")
    FOOTER = (By.XPATH, "//footer[@id='footer']")
    COOKIE_BUTTON = (By.ID, "wt-cli-accept-all-btn")

    @allure.step("Insider ana sayfası açılıyor")
    def open(self):
        self.driver.get(self.URL)
        self._accept_cookies()

    def _accept_cookies(self):
        try:
            self.click(self.COOKIE_BUTTON)
        except Exception:
            pass

    @allure.step("Ana sayfa yüklendi mi kontrol ediliyor")
    def is_home_page_loaded(self):
        return (
            "Insider" in self.driver.title and
            self.is_displayed(self.HEADER_MENU) and
            self.is_displayed(self.COMPANY_LOGO) and
            self.is_displayed(self.HERO_SECTION) and
            self.is_displayed(self.FOOTER)
        )
