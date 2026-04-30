import os
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException



class BasePage:
    DEFAULT_TIMEOUT = 15
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def get_text(self, locator):
        return self.find_element(locator).text

    def is_displayed(self, locator):
        try:
            return self.find_element(locator).is_displayed()
        except TimeoutException:
            return False

    def take_screenshot(self, name: str) -> str:
        os.makedirs("reports/screenshots", exist_ok=True)
        path = os.path.join("reports/screenshots", f"{name}.png")
        self.driver.save_screenshot(path)
        # Allure'a da attach edilir.
        with open(path, "rb") as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
        return path