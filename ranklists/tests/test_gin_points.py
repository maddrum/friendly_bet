from selenium.webdriver.common.by import By

from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase


class GinPointsTest(BrowserTestBase):
    @handle_failed_browser_test
    def test_no_data_gin_page(self):
        self.load_page(namespace="gin_total")
        self.assertEqual("АНГЕЛ-А", self.browser.find_element(By.CSS_SELECTOR, ".heading.inner-ttl").text)
        self.assertEqual(
            "Към момента информацията е кът.", self.browser.find_element(By.CLASS_NAME, "dummy--no__info").text
        )
