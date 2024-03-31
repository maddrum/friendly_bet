from unittest.mock import patch

from django.conf import settings
from django.utils import timezone
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from matches.models import Match
from predictions.models import UserPrediction
from predictions.tests.base import PredictionsBaseTestCase
from predictions.tools import add_user_predictions, create_invalid_prediction, create_valid_prediction
from predictions.views_mixins import GetEventMatchesMixin
from utlis.tests.browser_test_utils import handle_failed_browser_test


class TestPredictionsCreateUpdate(PredictionsBaseTestCase):
    @handle_failed_browser_test
    def test_create_prediction_form(self):
        for user in self.test_users:
            self.login_user(user=user)
            self.load_page(namespace="create_predictions")
            self.validate_submit_btn()
            self.validate_user_predictions(user=user, matches=self.mixin.matches)

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_try_to_create_prediction_for_started_match(self, mocked_datetime):
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        self.load_page(namespace="create_predictions")
        submit = self.validate_submit_btn()
        counter = 0
        for match in self.mixin.matches:
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            counter += 1

        match = self.mixin.matches.first()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH - 1
        mocked_datetime.return_value = match.match_start_time - timezone.timedelta(minutes=delta_minutes)
        submit.send_keys(Keys.RETURN)
        self.assertEqual(self.test_users[0].predictions.all().count(), 0)
        self.validate_404()

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_create_prediction_some_matches_started(self, mocked_datetime):
        mocked_datetime.return_value = Match.objects.first().match_start_time + timezone.timedelta(minutes=30)
        mixin = GetEventMatchesMixin(event=self.event)
        self.login_user(user=self.test_users[0])
        self.load_page(namespace="create_predictions")
        self.validate_user_predictions(matches=mixin.matches, user=self.test_users[0])
        self.assertEqual(self.test_users[0].predictions.all().count(), mixin.matches.count())
        self.assertNotEqual(self.test_users[0].predictions.all().count(), self.mixin.matches.count())

    @handle_failed_browser_test
    def test_update_prediction_form(self):
        add_user_predictions(event=self.event, users=0)
        for user in self.test_users:
            self.login_user(user=user)
            for prediction in user.predictions.all():
                if prediction.match not in self.mixin.matches:
                    break
                match = Match.objects.filter(pk=prediction.match.pk)
                self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
                self.validate_submit_btn()
                self.validate_user_predictions(user=user, matches=match)

    @handle_failed_browser_test
    def test_user_update_prediction_of_other_user(self):
        add_user_predictions(event=self.event, users=0)
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[1].predictions.all().first()
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
        self.validate_404()

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_update_prediction_of_started_match(self, mocked_datetime):
        add_user_predictions(event=self.event, users=0)
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        prediction_specs = [
            prediction.pk,
            prediction.match_state,
            prediction.goals_home,
            prediction.goals_guest,
        ]
        bet_additional_specs = [
            prediction.bet_points.pk,
            prediction.bet_points.apply_match_state,
            prediction.bet_points.apply_result,
        ]
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
        submit = self.validate_submit_btn()

        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH - 1
        mocked_datetime.return_value = prediction.match.match_start_time - timezone.timedelta(minutes=delta_minutes)
        while True:
            prediction_data = create_valid_prediction()
            if prediction_data.event_match_state == prediction.match_state:
                continue
            break

        self.fill_in_prediction(form_id="0", prediction=prediction_data)
        submit.send_keys(Keys.RETURN)
        prediction = UserPrediction.objects.get(pk=prediction_specs[0])
        self.assertEqual(prediction.match_state, prediction_specs[1])
        self.assertEqual(prediction.goals_home, prediction_specs[2])
        self.assertEqual(prediction.goals_guest, prediction_specs[3])
        self.assertEqual(prediction.bet_points.apply_match_state, bet_additional_specs[1])
        self.assertEqual(prediction.bet_points.apply_result, bet_additional_specs[2])
        self.validate_submit_btn(should_have_submit_btn=False)
        self.validate_404()

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_update_prediction_of_not_started_match(self, mocked_datetime):
        add_user_predictions(event=self.event, users=0)
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        prediction_specs = [
            prediction.pk,
            prediction.match_state,
            prediction.goals_home,
            prediction.goals_guest,
        ]
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
        submit = self.validate_submit_btn()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH + 1
        mocked_datetime.return_value = prediction.match.match_start_time - timezone.timedelta(minutes=delta_minutes)
        while True:
            prediction_data = create_valid_prediction()
            if prediction_data.event_match_state == prediction.match_state:
                continue
            break

        self.fill_in_prediction(form_id="0", prediction=prediction_data)

        submit.send_keys(Keys.RETURN)
        prediction = UserPrediction.objects.get(pk=prediction_specs[0])
        self.assertNotEqual(prediction.match_state, prediction_specs[1])
        self.validate_submit_btn(should_have_submit_btn=False)

    @handle_failed_browser_test
    def test_invalid_form_check(self):
        self.login_user(user=self.test_users[0])
        self.load_page(namespace="create_predictions")
        wrong_prediction_match = 0
        for match in self.mixin.matches:
            counter = 0
            for match in self.mixin.matches:
                if wrong_prediction_match == counter:
                    prediction_data = create_invalid_prediction()
                    self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
                else:
                    prediction_data = create_valid_prediction()
                    self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
                counter += 1

            submit = self.browser.find_elements(By.CSS_SELECTOR, "input[type=submit]")[0]
            submit.send_keys(Keys.RETURN)
            wrong_prediction_match += 1
        self.assertEqual(self.test_users[0].predictions.all().count(), 0)

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_update_prediction_valid_apply_match_state_initial_value(self, mocked_datetime):
        add_user_predictions(event=self.event, users=0)
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH + 1
        mocked_datetime.return_value = prediction.match.match_start_time - timezone.timedelta(minutes=delta_minutes)
        # validate applied
        bet_points_obj = prediction.bet_points
        bet_points_obj.apply_match_state = True
        bet_points_obj.save()
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
        checkbox = self.browser.find_element(By.NAME, "form-0-accept_match_state_bet")
        self.assertTrue(checkbox.is_selected())
        # validate not applied
        bet_points_obj = prediction.bet_points
        bet_points_obj.apply_match_state = False
        bet_points_obj.save()
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk})
        checkbox = self.browser.find_element(By.NAME, "form-0-accept_match_state_bet")
        self.assertFalse(checkbox.is_selected())

    def test_must_be_logged_in_to_update_prediction(self):
        self.load_page(namespace="update_prediction", reverse_kwargs={"pk": 1})
        self.validate_404()