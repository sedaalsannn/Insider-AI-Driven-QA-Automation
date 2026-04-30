import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base.base_page import BasePage


class LeverPage(BasePage):

    DEPARTMENT_TITLE = (By.CSS_SELECTOR, ".posting-category-title.large-category-label")
    JOB_ITEMS        = (By.CSS_SELECTOR, ".posting")
    JOB_TITLE        = (By.CSS_SELECTOR, "h5[data-qa='posting-name']")
    JOB_LOCATION     = (By.CSS_SELECTOR, ".sort-by-location")
    APPLY_BUTTON = (By.CSS_SELECTOR, "[data-qa='btn-apply']")

    # --- Detay sayfası locators (Image 2) ---
    DETAIL_JOB_TITLE = (By.CSS_SELECTOR, "div.posting-headline h2")
    DETAIL_LOCATION = (By.CSS_SELECTOR, ".sort-by-time.location")
    DETAIL_CATEGORIES = (By.CSS_SELECTOR, "div.posting-categories div[class*='posting-category']")
    APPLY_FOR_THIS_JOB = (By.CSS_SELECTOR, "a.postings-btn.template-btn-submit")

    def is_lever_page(self):
        return "lever.co" in self.driver.current_url

    def is_lever_apply_page(self):
        url = self.driver.current_url
        return "jobs.lever.co/insiderone" in url and "?" not in url

    def get_department_title(self):
        return self.get_text(self.DEPARTMENT_TITLE)

    def wait_for_jobs(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(self.JOB_ITEMS)
        )

    def get_jobs(self):
        jobs_data = []
        jobs = self.driver.find_elements(*self.JOB_ITEMS)
        for job in jobs:
            try:
                title    = job.find_element(*self.JOB_TITLE).text
                location = job.find_element(*self.JOB_LOCATION).text
                jobs_data.append({"title": title, "location": location})
            except Exception:
                continue
        return jobs_data

    def get_istanbul_jobs(self):
        return [j for j in self.get_jobs() if "istanbul" in j["location"].lower()]

    def click_apply_first_job(self):
        buttons = self.driver.find_elements(*self.APPLY_BUTTON)
        if not buttons:
            raise Exception("Apply button bulunamadı")
        button = buttons[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
        time.sleep(0.5)
        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)

    # --- Detay sayfası metodları (Image 2) ---
    def wait_for_apply_page(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.DETAIL_JOB_TITLE)
        )

    def get_detail_categories(self):
        elements = self.driver.find_elements(*self.DETAIL_CATEGORIES)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_detail_location(self):
        return self.get_text(self.DETAIL_LOCATION)

    def assert_department_is_qa(self):
        categories = self.get_detail_categories()
        assert any("quality assurance" in c.lower() for c in categories), (
            f"Kategorilerde 'Quality Assurance' bulunamadı: {categories}"
        )

    def assert_location_is_istanbul(self):
        location = self.get_detail_location()
        assert "istanbul" in location.lower(), (
            f"Lokasyonda 'Istanbul' yok: '{location}'"
        )

    def assert_apply_button_visible(self):
        assert self.is_displayed(self.APPLY_FOR_THIS_JOB), (
            "'APPLY FOR THIS JOB' butonu görünür değil!"
        )

