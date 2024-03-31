import time

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.urls import reverse
from selenium import webdriver
from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


@override_settings(DEBUG=True)
class BrowserTestBase(StaticLiveServerTestCase):
    browser = None
    host = settings.TEST_SERVER_HOST

    def setUp(self):
        super().setUp()
        self._browser_setup()

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

    def _browser_setup(self):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        # directory /home/seluser/Downloads is a volume in docker-compose.tests and docker-compose.tests.hub
        # /home/seluser is the home folder of the user in selenium container,
        # download dir is set so that user has rights to write inside it
        _selenium_user_home_folder = r"/home/seluser/Downloads"
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": _selenium_user_home_folder,
                "savefile.default_directory": _selenium_user_home_folder,
                "directory_upgrade": True,
                "safebrowsing.enabled": True,
                "download.prompt_for_download": False,
            },
        )

        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=options,
        )

        self.load_page(namespace="index")

    def login_user(self, user):
        self.client.login(username=user.username, password="qqwerty123")
        cookie = self.client.cookies["sessionid"]
        session_cookie = {
            "name": settings.SESSION_COOKIE_NAME,
            "value": cookie.value,
            "secure": False,
            "path": "/",
        }
        self.browser.delete_cookie(settings.SESSION_COOKIE_NAME)
        self.browser.add_cookie(session_cookie)

    def logout_user(self):
        self.browser.delete_cookie(settings.SESSION_COOKIE_NAME)

    def assert_on_login_page(self):
        self.assertEqual("влез", self.browser.find_element(By.CSS_SELECTOR, ".heading.inner-ttl"))

    def validate_submit_btn(self, should_have_submit_btn=True):
        submit = self.browser.find_elements(By.CSS_SELECTOR, "input[type=submit]")
        if should_have_submit_btn:
            self.assertEqual(len(submit), 1)
            return submit[0]
        self.assertEqual(len(submit), 0)
        return None

    def validate_404(self):
        self.assertEqual("Page not found (404)", self.browser.find_element(By.TAG_NAME, "h1").text.strip())
        self.validate_submit_btn(should_have_submit_btn=False)

    def get_full_url(self, namespace: str, reverse_kwargs):
        return f"{self.live_server_url}{reverse(namespace, kwargs=reverse_kwargs)}"

    def load_page(self, namespace: str, reverse_kwargs: dict = None):
        self.browser.get(self.get_full_url(namespace=namespace, reverse_kwargs=reverse_kwargs))

    def action_chain_click(self, element: WebElement):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        actions = ActionChains(self.browser)
        actions.move_to_element(element)
        actions.click(element)
        actions.perform()

    def move_to_element(self, element: WebElement):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)

    def click_captcha(self):
        captcha = self.browser.find_element(
            By.CSS_SELECTOR,
            'iframe[name^="a-"][src^="https://www.google.com/recaptcha/api2/anchor?"]',
        )
        self.browser.switch_to.frame(captcha)
        self.action_chain_click(self.browser.find_element(By.XPATH, '//span[@id="recaptcha-anchor"]'))
        time.sleep(1)
        self.browser.switch_to.default_content()
