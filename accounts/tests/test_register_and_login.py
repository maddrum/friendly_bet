import logging
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from accounts.model_factories import UserFactory
from matches.tools import initialize_matches
from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase

logger = logging.getLogger("friendly_bet")


class RegisterLoginLogoutTests(BrowserTestBase):
    event = None
    temp_user_1 = None
    temp_user_2 = None

    def setUp(self):
        super().setUp()
        UserFactory.reset_sequence()
        self.event = initialize_matches()
        self.temp_user_1 = UserFactory()
        self.temp_user_2 = UserFactory()

    def register_helper(self, username, password_1, password_2):
        self.load_page(namespace="register")
        username_field = self.browser.find_element(By.ID, "id_username")
        password_field = self.browser.find_element(By.ID, "id_password1")
        password_field_2 = self.browser.find_element(By.ID, "id_password2")
        username_field.send_keys(username)
        password_field.send_keys(password_1)
        password_field_2.send_keys(password_2)
        self.click_captcha()
        submit = self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]")
        submit.click()

    def login_helper(self, username, password):
        self.load_page(namespace="login")
        username_field = self.browser.find_element(By.ID, "id_username")
        password_field = self.browser.find_element(By.ID, "id_password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit = self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]")
        submit.send_keys(Keys.RETURN)

    @handle_failed_browser_test
    def test_register_user_ok(self):
        username = "test_username"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2=password)
        created_user = get_user_model().objects.filter(username=username).first()
        self.assertIsNotNone(created_user)

    @handle_failed_browser_test
    def test_register_user_no_password_match(self):
        username = "test_username"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2="testtest")
        created_user = get_user_model().objects.filter(username=username).first()
        self.assertIsNone(created_user)
        self.assertNotEqual(len(self.browser.find_elements(By.CSS_SELECTOR, ".error")), 0)

    @handle_failed_browser_test
    def test_user_is_taken(self):
        username = "user_0"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2=password)
        self.assertNotEqual(len(self.browser.find_elements(By.CSS_SELECTOR, ".error")), 0)

    @handle_failed_browser_test
    def test_logout_user(self):
        self.login_user(user=self.temp_user_1)
        self.load_page(namespace="profile")
        self.assertIsNotNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--logout__button"))
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--logout__confirm"))
        time.sleep(1)
        self.assertIsNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))

    @handle_failed_browser_test
    def test_login_user(self):
        user = UserFactory()

        self.assertIsNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))
        self.login_helper(username=user.username, password="qqwerty1234")
        self.assertIsNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))
        self.browser.find_element(By.CSS_SELECTOR, "div.error-message")

        self.login_helper(username="random-username", password="qqwerty123")
        self.assertIsNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))
        self.browser.find_element(By.CSS_SELECTOR, "div.error-message")

        self.login_helper(username=user.username, password="qqwerty123")
        self.assertIsNotNone(self.browser.get_cookie(settings.SESSION_COOKIE_NAME))
