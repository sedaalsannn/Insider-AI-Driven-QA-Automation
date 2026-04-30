import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base.base_page import BasePage


class CareerPage(BasePage):
    URL = "https://insiderone.com/careers/#open-roles"

    SEE_ALL_TEAMS = (By.XPATH, "//a[normalize-space()='See all teams']")
    QA_OPEN_POSITIONS = (By.CSS_SELECTOR, "a.insiderone-icon-cards-grid-item-btn[href*='Quality%20Assurance']")

    def open(self):
        self.driver.get(self.URL)

    def click_see_all_teams(self):
        try:
            self.click(self.SEE_ALL_TEAMS)
            # Kartların açılma animasyonu için beklenir
            time.sleep(2)
        except Exception:
            pass

    def click_qa_open_positions(self):
        # 1. Önce "See all teams" sonrası container açılmış mı kontrol edilir.
        wait = WebDriverWait(self.driver, 20)

        # Element clickable olana kadar beklenir.
        element = wait.until(EC.element_to_be_clickable(self.QA_OPEN_POSITIONS))

        # Scroll into view + animasyonun bitmesini bekle
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
            element
        )
        time.sleep(1.5)  # CSS transition'ın bitmesi için

        # href'i al — eğer varsa ve geçerliyse direkt navigate edilir.
        href = element.get_attribute("href")
        if href and "lever.co" in href:
            self.driver.get(href)
            return

        # href yoksa veya beklenenden farklıysa JS click'e düş
        self.driver.execute_script("arguments[0].click();", element)