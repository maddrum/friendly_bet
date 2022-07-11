import os
from unittest.mock import patch

from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from accounts.model_factories import UserFactory
from main_app.object_tools import add_user_predictions, create_valid_prediction, initialize_event
from matches.models import Match
from predictions.models import UserPrediction
from predictions.views_mixins import GetEventMatchesMixin


class PredictionsCreateUpdateTest(LiveServerTestCase):
    test_users = None
    driver = None
    event = None
    mixin = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        driver_path = os.path.join(settings.BASE_DIR, '__web_driver') + '/chromedriver'
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(driver_path, options=chrome_options)
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

    def validate_submit_btn(self, should_have_submit_btn=True):
        submit = self.driver.find_elements(By.CSS_SELECTOR, 'input[type=submit]')
        if should_have_submit_btn:
            self.assertEqual(len(submit), 1)
            return submit[0]
        self.assertEqual(len(submit), 0)
        return None

    def validate_404(self):
        self.validate_submit_btn(should_have_submit_btn=False)
        value = self.driver.find_element(By.ID, '404-page').text
        self.assertEqual(value, 'ЗАСАДА 404!')

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
            self.validate_submit_btn()
            self.validate_user_predictions(user=user, matches=self.mixin.matches)

    @patch('predictions.views_mixins.GetEventMatchesMixin._get_current_time')
    def test_user_try_to_create_prediction_for_started_match(self, mocked_datetime):
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        predictions_url = reverse('create_predictions')
        self.driver.get(f'{self.live_server_url}{predictions_url}')
        submit = self.validate_submit_btn()
        counter = 0
        for match in self.mixin.matches:
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            counter += 1

        match = self.mixin.matches.first()
        mocked_datetime.return_value = match.match_start_time + timezone.timedelta(minutes=30)
        submit.send_keys(Keys.RETURN)
        self.assertEqual(self.test_users[0].predictions.all().count(), 0)
        self.validate_404()

    @patch('predictions.views_mixins.GetEventMatchesMixin._get_current_time')
    def test_user_create_prediction_some_matches_started(self, mocked_datetime):
        mocked_datetime.return_value = Match.objects.first().match_start_time + timezone.timedelta(minutes=30)
        mixin = GetEventMatchesMixin(event=self.event)
        self.login_user(user=self.test_users[0])
        predictions_url = reverse('create_predictions')
        self.driver.get(f'{self.live_server_url}{predictions_url}')
        self.validate_user_predictions(matches=mixin.matches, user=self.test_users[0])
        self.assertEqual(self.test_users[0].predictions.all().count(), mixin.matches.count())
        self.assertNotEqual(self.test_users[0].predictions.all().count(), self.mixin.matches.count())

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
                self.validate_submit_btn()
                self.validate_user_predictions(user=user, matches=match)

    def test_user_update_prediction_of_other_user(self):
        add_user_predictions(event=self.event, users=0)
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[1].predictions.all().first()
        predictions_url = reverse('update_prediction', kwargs={'pk': prediction.pk})
        self.driver.get(f'{self.live_server_url}{predictions_url}')
        self.validate_404()

    @patch('predictions.views_mixins.GetEventMatchesMixin._get_current_time')
    def test_user_update_prediction_of_started_match(self, mocked_datetime):
        add_user_predictions(event=self.event, users=0)
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        prediction_specs = [prediction.pk, prediction.match_state, prediction.goals_home, prediction.goals_guest]
        bet_additional_specs = [prediction.bet_points.pk, prediction.bet_points.apply_match_state,
                                prediction.bet_points.apply_result]
        predictions_url = reverse('update_prediction', kwargs={'pk': prediction.pk})
        self.driver.get(f'{self.live_server_url}{predictions_url}')
        submit = self.validate_submit_btn()
        mocked_datetime.return_value = prediction.match.match_start_time + timezone.timedelta(minutes=30)
        while True:
            prediction_data = create_valid_prediction()
            if prediction_data[1] == prediction.match_state.match_state:
                continue
            break

        self.fill_in_prediction(form_id='0', prediction=prediction_data)
        submit.send_keys(Keys.RETURN)
        prediction = UserPrediction.objects.get(pk=prediction_specs[0])
        self.assertEqual(prediction.match_state, prediction_specs[1])
        self.assertEqual(prediction.goals_home, prediction_specs[2])
        self.assertEqual(prediction.goals_guest, prediction_specs[3])
        self.assertEqual(prediction.bet_points.apply_result, bet_additional_specs[1])
        self.assertEqual(prediction.bet_points.apply_match_state, bet_additional_specs[2])
        self.validate_submit_btn(should_have_submit_btn=False)
        self.validate_404()

    @patch('predictions.views_mixins.GetEventMatchesMixin._get_current_time')
    def test_user_update_prediction_of_not_started_match(self, mocked_datetime):
        add_user_predictions(event=self.event, users=0)
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        prediction_specs = [prediction.pk, prediction.match_state, prediction.goals_home, prediction.goals_guest]
        predictions_url = reverse('update_prediction', kwargs={'pk': prediction.pk})
        self.driver.get(f'{self.live_server_url}{predictions_url}')
        submit = self.validate_submit_btn()
        mocked_datetime.return_value = prediction.match.match_start_time - timezone.timedelta(minutes=30)
        while True:
            prediction_data = create_valid_prediction()
            if prediction_data[1] == prediction.match_state.match_state:
                continue
            break

        self.fill_in_prediction(form_id='0', prediction=prediction_data)

        submit.send_keys(Keys.RETURN)
        prediction = UserPrediction.objects.get(pk=prediction_specs[0])
        self.assertNotEqual(prediction.match_state, prediction_specs[1])
        self.validate_submit_btn(should_have_submit_btn=False)
