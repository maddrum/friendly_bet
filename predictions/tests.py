import os

from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from accounts.model_factories import UserFactory
from main_app.object_tools import create_valid_prediction, initialize_event
from predictions.views_mixins import GetEventMatchesMixin


class PlayerFormTest(LiveServerTestCase):
    test_users = None
    driver = None
    event = None
    mixin = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        driver_path = os.path.join(settings.BASE_DIR, '__web_driver') + '/chromedriver'
        cls.driver = webdriver.Chrome(driver_path)
        cls.driver.implicitly_wait(10)

    def setUp(self) -> None:
        self.test_users = []
        for item in range(5):
            temp_user = UserFactory()
            temp_user.set_password('qqwerty123')
            temp_user.save()
            self.test_users.append(temp_user)
        self.event = initialize_event()
        self.mixin = GetEventMatchesMixin(event=self.event)
        self.driver.get(self.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login_user(self, user):
        self.client.login(username=user.username, password='qqwerty123')
        cookie = self.client.cookies['sessionid']
        session_cookie = {
            'name': settings.SESSION_COOKIE_NAME,
            'value': cookie.value,
            'secure': False,
            'path': '/',
        }
        self.driver.add_cookie(session_cookie)

    def fill_in_prediction(self, form_id, prediction):
        match_state_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-match_state')
        match_state_selector = Select(match_state_element)
        match_state_selector.select_by_value(str(prediction[1]))

        home_score_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-goals_home')
        home_score_element.send_keys(Keys.DELETE, prediction[2])

        guest_score_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-goals_guest')
        guest_score_element.send_keys(Keys.DELETE, prediction[3])

    def test_create_prediction_form(self):
        for user in self.test_users:
            self.login_user(user=user)
            predictions_url = reverse('create_predictions')
            self.driver.get(f'{self.live_server_url}{predictions_url}')
            for form_id in range(self.mixin.matches.count()):
                prediction_data = create_valid_prediction()
                self.fill_in_prediction(form_id=str(form_id), prediction=prediction_data)

            submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type=submit]')[0]

            # submit form
            submit.send_keys(Keys.RETURN)
