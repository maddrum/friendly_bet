import time

from faker import Faker
from selenium.webdriver.common.by import By

from main_app.models import SiteContact
from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase

fake = Faker()


class MainAppTests(BrowserTestBase):
    def test_instruction_page_works(self):
        self.load_page(namespace="instructions")
        self.browser.find_element(By.CSS_SELECTOR, ".dummy--instruction__title")

    @handle_failed_browser_test
    def test_contact_page(self):
        self.assertIsNone(SiteContact.objects.all().first())
        self.load_page(namespace="contact")
        name = fake.name()
        email = fake.email()
        question = fake.sentence(nb_words=5)
        self.browser.find_element(By.ID, "id_message").send_keys(question)
        self.browser.find_element(By.ID, "id_name").send_keys(name)
        self.browser.find_element(By.ID, "id_email").send_keys(email)
        self.click_captcha()
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]"))

        time.sleep(1)
        obj = SiteContact.objects.all().first()
        self.assertIsNotNone(obj)
        self.assertEqual(name, obj.name)
        self.assertEqual(email, obj.email)
        self.assertEqual(question, obj.message)

        self.assertEqual(
            "Вашето запитване е получено! Ще отговорим при първа възможност или ще го пропуснем ако е тъпо.",
            self.browser.find_element(By.TAG_NAME, "h4").text,
        )
