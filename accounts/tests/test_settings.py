import time

from faker import Faker
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from accounts.model_factories import UserFactory
from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase

fake = Faker()


class TestAccountSettings(BrowserTestBase):
    user = None

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.login_user(user=self.user)
        self.load_page(namespace="profile_settings")

    @handle_failed_browser_test
    def test_change_name(self):
        name = fake.first_name()
        last_name = fake.last_name()
        self.browser.find_element(By.ID, "id_first_name").clear()
        self.browser.find_element(By.ID, "id_first_name").send_keys(name)

        self.browser.find_element(By.ID, "id_last_name").clear()
        self.browser.find_element(By.ID, "id_last_name").send_keys(last_name)

        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--submit__button"))
        time.sleep(0.5)

        self.user.refresh_from_db()
        self.assertEqual(name, self.user.first_name)
        self.assertEqual(last_name, self.user.last_name)

    def test_change_password_success(self):
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--password__change"))
        time.sleep(0.5)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        old_password = self.browser.find_element(By.ID, "id_old_password")
        new_password_1 = self.browser.find_element(By.ID, "id_new_password1")
        new_password_2 = self.browser.find_element(By.ID, "id_new_password2")
        old_password.clear()
        old_password.send_keys("qqwerty123")
        new_password_1.clear()
        new_password_1.send_keys("qqwerty1234")
        new_password_2.clear()
        new_password_2.send_keys("qqwerty1234")
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--submit__button"))
        time.sleep(0.5)

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("qqwerty1234"))

    def test_change_password_wrong_current_password(self):
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--password__change"))
        time.sleep(0.5)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        old_password = self.browser.find_element(By.ID, "id_old_password")
        new_password_1 = self.browser.find_element(By.ID, "id_new_password1")
        new_password_2 = self.browser.find_element(By.ID, "id_new_password2")
        old_password.clear()
        old_password.send_keys("aba-bala")
        new_password_1.clear()
        new_password_1.send_keys("qqwerty1234")
        new_password_2.clear()
        new_password_2.send_keys("qqwerty1234")
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--submit__button"))
        time.sleep(0.5)

        self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("qqwerty1234"))

    def test_change_password_passwords_dont_match(self):
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--password__change"))
        time.sleep(0.5)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        old_password = self.browser.find_element(By.ID, "id_old_password")
        new_password_1 = self.browser.find_element(By.ID, "id_new_password1")
        new_password_2 = self.browser.find_element(By.ID, "id_new_password2")
        old_password.clear()
        old_password.send_keys("qqwerty123")
        new_password_1.clear()
        new_password_1.send_keys("qqwerty12345")
        new_password_2.clear()
        new_password_2.send_keys("qqwerty1234")
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, ".dummy--submit__button"))
        time.sleep(0.5)

        self.browser.find_element(By.CSS_SELECTOR, "ul.errorlist")
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("qqwerty1234"))
        self.assertFalse(self.user.check_password("qqwerty12345"))
