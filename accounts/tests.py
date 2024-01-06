import logging
import time

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from accounts.model_factories import UserFactory
from matches.tools import initialize_matches
from utlis.tests.browser_tests import BrowserTestBase

logger = logging.getLogger("friendly_bet")


class RegisterLoginUserTest(BrowserTestBase):
    event = None
    temp_user_1 = None
    temp_user_2 = None

    def setUp(self):
        UserFactory.reset_sequence()
        self.event = initialize_matches()
        self.temp_user_1 = UserFactory()
        self.temp_user_2 = UserFactory()

    def register_helper(self, username, password_1, password_2):
        self.driver.get(f'{self.live_server_url}{reverse("register")}')
        username_field = self.driver.find_element(By.ID, "id_username")
        password_field = self.driver.find_element(By.ID, "id_password1")
        password_field_2 = self.driver.find_element(By.ID, "id_password2")
        username_field.send_keys(username)
        password_field.send_keys(password_1)
        password_field_2.send_keys(password_2)
        # captcha
        captcha = self.driver.find_element(
            By.CSS_SELECTOR,
            'iframe[name^="a-"][src^="https://www.google.com/recaptcha/api2/anchor?"]',
        )
        self.driver.switch_to.frame(captcha)
        self.driver.find_element(By.XPATH, '//span[@id="recaptcha-anchor"]').click()
        time.sleep(1)
        self.driver.switch_to.default_content()

        submit = self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]")
        submit.click()

    def login_helper(self, username, password):
        self.driver.get(f'{self.live_server_url}{reverse("login")}')
        username_field = self.driver.find_element(By.ID, "id_username")
        password_field = self.driver.find_element(By.ID, "id_password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit = self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]")
        submit.send_keys(Keys.RETURN)

    def test_register_user_ok(self):
        username = "test_username"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2=password)
        created_user = get_user_model().objects.filter(username=username).first()
        self.assertIsNotNone(created_user)

    def test_register_user_no_password_match(self):
        username = "test_username"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2="testtest")
        created_user = get_user_model().objects.filter(username=username).first()
        self.assertIsNone(created_user)
        self.assertNotEqual(len(self.driver.find_elements(By.CSS_SELECTOR, ".error")), 0)

    def test_user_is_taken(self):
        username = "user_0"
        password = "qqwerty1234"
        self.register_helper(username=username, password_1=password, password_2=password)
        self.assertNotEqual(len(self.driver.find_elements(By.CSS_SELECTOR, ".error")), 0)

    def test_login_user(self):
        self.login_helper(self.temp_user_2.username, password="qqwerty123")
        session = Session.objects.get(session_key=self.driver.get_cookie("sessionid")["value"])
        session_data = session.get_decoded()
        logged_user = get_user_model().objects.get(id=session_data.get("_auth_user_id"))
        self.assertTrue(logged_user.is_authenticated)
        self.assertEqual(self.temp_user_2, logged_user)
        self.assertNotEqual(self.temp_user_1, logged_user)

    def test_wrong_login_user(self):
        self.login_helper(self.temp_user_2.username, password="wrong_password")
        self.assertIsNone(self.driver.get_cookie("sessionid"))
        self.login_helper(username="dump_username", password="qqwerty123")
        self.assertIsNone(self.driver.get_cookie("sessionid"))
