import chromedriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from django.conf import settings
from selenium.webdriver.common.by import By


class BrowserTestBase(StaticLiveServerTestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        if hasattr(settings, "HEADLESS") and settings.HEADLESS:
            chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login_user(self, user):
        self.client.login(username=user.username, password="qqwerty123")
        cookie = self.client.cookies["sessionid"]
        session_cookie = {
            "name": settings.SESSION_COOKIE_NAME,
            "value": cookie.value,
            "secure": False,
            "path": "/",
        }
        self.driver.delete_cookie(settings.SESSION_COOKIE_NAME)
        self.driver.add_cookie(session_cookie)

    def validate_submit_btn(self, should_have_submit_btn=True):
        submit = self.driver.find_elements(By.CSS_SELECTOR, "input[type=submit]")
        if should_have_submit_btn:
            self.assertEqual(len(submit), 1)
            return submit[0]
        self.assertEqual(len(submit), 0)
        return None

    def validate_404(self):
        self.validate_submit_btn(should_have_submit_btn=False)
        value = self.driver.find_element(By.ID, "404-page").text
        self.assertEqual(value, "ЗАСАДА 404!")
