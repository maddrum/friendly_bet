import os

from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from accounts.model_factories import UserFactory
from main_app.object_tools import add_user_predictions, create_valid_prediction, initialize_event
from matches.models import Match
from predictions.models import UserPrediction
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
        for item in range(10):
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
        self.driver.delete_cookie(settings.SESSION_COOKIE_NAME)
        self.driver.add_cookie(session_cookie)

    def fill_in_prediction(self, form_id, prediction):
        match_state_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-match_state')
        match_state_selector = Select(match_state_element)
        match_state_selector.select_by_value(str(prediction[1]))

        home_score_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-goals_home')
        home_score_element.clear()
        home_score_element.send_keys(prediction[2])

        guest_score_element = self.driver.find_element(By.ID, f'id_form-{str(form_id)}-goals_guest')
        guest_score_element.clear()
        guest_score_element.send_keys(prediction[3])

        apply_match_state = self.driver.find_element(By.ID, f'id_form-{form_id}-accept_match_state_bet')
        if prediction[5]:
            apply_match_state.click()

        apply_result = self.driver.find_element(By.ID, f'id_form-{form_id}-accept_match_result_bet')
        if prediction[6]:
            apply_result.click()

    def validate_user_predictions(self, user, matches):
        matches_prediction = {}
        counter = 0
        for match in matches:
            # input prediction is driven by the matches which are ordered like
            # GetEventMatchesMixin. This is simulation of so.
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            matches_prediction[match] = prediction_data
            counter += 1
        submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type=submit]')[0]
        submit.send_keys(Keys.RETURN)

        for match in matches:
            given_prediction = matches_prediction[match]
            prediction_qs = UserPrediction.objects.filter(user=user, match=match)
            self.assertEqual(prediction_qs.count(), 1)
            prediction = prediction_qs.first()
            self.assertEqual(prediction.match_state.match_state, given_prediction[0])
            self.assertEqual(prediction.goals_home, given_prediction[2])
            self.assertEqual(prediction.goals_guest, given_prediction[3])
            bet_points = prediction.bet_points
            self.assertEqual(bet_points.apply_match_state, given_prediction[5])
            self.assertEqual(bet_points.apply_result, given_prediction[6])
            bet_points.points_match_state_to_take = prediction.match.phase.bet_points.points_state
            bet_points.points_match_state_to_give = prediction.match.phase.bet_points.return_points_state
            bet_points.points_result_to_take = prediction.match.phase.bet_points.points_result
            bet_points.points_result_to_give = prediction.match.phase.bet_points.return_points_result

    def test_create_prediction_form(self):
        for user in self.test_users:
            self.login_user(user=user)
            predictions_url = reverse('create_predictions')
            self.driver.get(f'{self.live_server_url}{predictions_url}')
            self.validate_user_predictions(user=user, matches=self.mixin.matches)

    def user_try_to_create_prediction_for_started_match(self):
        pass

    def test_update_prediction_form(self):
        add_user_predictions(event=self.event, users=0)
        for user in self.test_users:
            self.login_user(user=user)
            for prediction in user.predictions.all():
                if prediction.match not in self.mixin.matches:
                    break
                match = Match.objects.filter(pk=prediction.match.pk)
                predictions_url = reverse('update_prediction', kwargs={'pk': prediction.pk})
                self.driver.get(f'{self.live_server_url}{predictions_url}')
                self.validate_user_predictions(user=user, matches=match)

    def test_user_update_prediction_of_other_user(self):
        pass

    def test_user_update_prediction_of_started_match(self):
        pass
