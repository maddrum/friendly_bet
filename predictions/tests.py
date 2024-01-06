import logging
import random
from unittest.mock import patch

import chromedriver_autoinstaller
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
from events.models import EventMatchState
from events.settings import ALL_MATCH_STATES_LIST
from matches.models import Match, MatchResult
from matches.tools import initialize_matches
from predictions.models import (
    BetAdditionalPoint,
    PredictionPoint,
    UserPrediction,
    UserScore,
)
from predictions.tools import (
    add_user_predictions,
    create_invalid_prediction,
    create_valid_prediction,
    generate_valid_goals_by_match_state,
    PredictionDTO,
)
from predictions.views_mixins import GetEventMatchesMixin

logger = logging.getLogger("friendly_bet")
logger.propagate = False


class UserPredictionsToolBox:
    _generate_methods = {
        "generate_match_prediction_nothing_guessed": "Nothing guessed -> 1 pt",
        "generate_match_prediction_guessed_state": "Guessed state -> 4 pt",
        "generate_match_prediction_guessed_result": "Guessed result -> 9 pt",
    }

    @staticmethod
    def handle_user_prediction_bet_points(
        user_prediction, guessed_state=False, guessed_result=False
    ):
        extra_points = 0
        bet_points = user_prediction.bet_points
        if bet_points.apply_match_state:
            if guessed_state:
                extra_points += bet_points.points_match_state_to_give
            else:
                extra_points -= bet_points.points_match_state_to_take

        if bet_points.apply_result:
            if guessed_result:
                extra_points += bet_points.points_result_to_give
            else:
                extra_points -= bet_points.points_result_to_take

        return extra_points

    @staticmethod
    def create_user_prediction(
        user, match, apply_result=False, apply_match_state=False
    ):
        match_state = random.choice(ALL_MATCH_STATES_LIST)
        state = EventMatchState.objects.get(match_state=match_state)
        goals_home, goals_guest = generate_valid_goals_by_match_state(
            match_state=match_state
        )
        user_prediction = UserPrediction.objects.create(
            user=user,
            match=match,
            match_state=state,
            goals_home=goals_home,
            goals_guest=goals_guest,
        )
        bet_points = BetAdditionalPoint.objects.create(
            prediction=user_prediction,
            apply_result=apply_result,
            apply_match_state=apply_match_state,
            points_match_state_to_take=4,
            points_result_to_take=10,
            points_match_state_to_give=11,
            points_result_to_give=21,
        )
        return user_prediction, bet_points

    @staticmethod
    def get_match_result_obj(match):
        match_result = MatchResult.objects.filter(match=match).first()
        if match_result is None:
            match_state = EventMatchState.objects.get(
                match_state=random.choice(ALL_MATCH_STATES_LIST)
            )
            match_result = MatchResult.objects.create(
                match=match, match_state=match_state
            )
        match_result.match_is_over = False
        match_result.save()
        return match_result

    def generate_match_prediction_nothing_guessed(
        self, user_prediction, base_points_only=True
    ):
        return_points = 1
        state = user_prediction.match_state
        while True:
            other_match_state = random.choice(ALL_MATCH_STATES_LIST)
            other_state = EventMatchState.objects.get(match_state=other_match_state)
            if other_state != state:
                break
        result_goals_home, result_goals_guest = generate_valid_goals_by_match_state(
            match_state=other_match_state
        )
        match_result = self.get_match_result_obj(match=user_prediction.match)
        match_result.match_state = other_state
        # deliberately left goals okay, if match state is wrong, no points should be received
        # despite the right goals
        match_result.score_home = result_goals_home
        match_result.score_guest = result_goals_guest
        match_result.match_is_over = True
        match_result.save()
        # extra bet points
        if not base_points_only:
            return_points += self.handle_user_prediction_bet_points(
                user_prediction=user_prediction
            )
        return return_points

    def generate_match_prediction_guessed_state(
        self, user_prediction, base_points_only=True
    ):
        return_points = 4
        match_result = self.get_match_result_obj(match=user_prediction.match)
        match_result.match_state = user_prediction.match_state
        match_result.score_home = user_prediction.goals_home + 1
        match_result.score_guest = user_prediction.goals_guest
        match_result.match_is_over = True
        match_result.save()
        # extra bet points
        if not base_points_only:
            return_points += self.handle_user_prediction_bet_points(
                user_prediction=user_prediction, guessed_state=True
            )
        return return_points

    def generate_match_prediction_guessed_result(
        self, user_prediction, base_points_only=True
    ):
        return_points = 9
        match_result = self.get_match_result_obj(match=user_prediction.match)
        match_result.match_state = user_prediction.match_state
        match_result.score_home = user_prediction.goals_home
        match_result.score_guest = user_prediction.goals_guest
        match_result.match_is_over = True
        match_result.save()
        # extra bet points
        if not base_points_only:
            return_points += self.handle_user_prediction_bet_points(
                user_prediction=user_prediction,
                guessed_state=True,
                guessed_result=True,
            )
        return return_points


class PredictionsBaseTestCase(LiveServerTestCase, UserPredictionsToolBox):
    test_users = None
    driver = None
    event = None
    mixin = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    def setUp(self) -> None:
        self.test_users = []
        for item in range(10):
            temp_user = UserFactory()
            temp_user.set_password("qqwerty123")
            temp_user.save()
            self.test_users.append(temp_user)
        self.event = initialize_matches()
        self.mixin = GetEventMatchesMixin(event=self.event)
        self.driver.get(self.live_server_url)

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

    def fill_in_prediction(self, form_id, prediction: PredictionDTO):
        match_state_element = self.driver.find_element(
            By.ID, f"id_form-{str(form_id)}-match_state"
        )
        match_state_selector = Select(match_state_element)
        match_state_selector.select_by_value(str(prediction.pk))

        home_score_element = self.driver.find_element(
            By.ID, f"id_form-{str(form_id)}-goals_home"
        )
        home_score_element.clear()
        home_score_element.send_keys(prediction.goals_home)

        guest_score_element = self.driver.find_element(
            By.ID, f"id_form-{str(form_id)}-goals_guest"
        )
        guest_score_element.clear()
        guest_score_element.send_keys(prediction.goals_guest)

        # clicks on bet points checkboxes until state is right
        checkbox_id = f"id_form-{form_id}-accept_match_state_bet"
        apply_match_state = self.driver.find_element(By.ID, checkbox_id)
        if apply_match_state.is_selected() != prediction.apply_match_state:
            self.driver.execute_script(
                f'document.querySelector("#{checkbox_id}").click()'
            )

        checkbox_id = f"id_form-{form_id}-accept_match_result_bet"
        apply_result = self.driver.find_element(By.ID, checkbox_id)
        if apply_result.is_selected() != prediction.apply_result:
            self.driver.execute_script(
                f'document.querySelector("#{checkbox_id}").click()'
            )

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

    def validate_user_predictions(self, user, matches):
        matches_prediction = {}
        counter = 0
        for match in matches:
            # validate apply initial state
            if not UserPrediction.objects.filter(user=user, match=match).exists():
                checkbox_state = self.driver.find_element(
                    By.NAME, f"form-{counter}-accept_match_state_bet"
                )
                checkbox_result = self.driver.find_element(
                    By.NAME, f"form-{counter}-accept_match_result_bet"
                )
                self.assertFalse(checkbox_state.is_selected())
                self.assertFalse(checkbox_result.is_selected())
            # input prediction is driven by the matches which are ordered like
            # GetEventMatchesMixin. This is simulation of so.
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            matches_prediction[match] = prediction_data
            counter += 1
        submit = self.driver.find_elements(By.CSS_SELECTOR, "input[type=submit]")[0]
        submit.send_keys(Keys.RETURN)

        for match in matches:
            given_prediction = matches_prediction[match]
            prediction_qs = UserPrediction.objects.filter(user=user, match=match)
            self.assertEqual(prediction_qs.count(), 1)
            prediction = prediction_qs.first()
            self.assertEqual(
                prediction.match_state.match_state, given_prediction.match_state
            )
            self.assertEqual(prediction.goals_home, given_prediction.goals_home)
            self.assertEqual(prediction.goals_guest, given_prediction.goals_guest)
            bet_points = prediction.bet_points
            self.assertEqual(
                bet_points.apply_match_state, given_prediction.apply_match_state
            )
            self.assertEqual(bet_points.apply_result, given_prediction.apply_result)
            bet_points.points_match_state_to_take = (
                prediction.match.phase.bet_points.points_state
            )
            bet_points.points_match_state_to_give = (
                prediction.match.phase.bet_points.return_points_state
            )
            bet_points.points_result_to_take = (
                prediction.match.phase.bet_points.points_result
            )
            bet_points.points_result_to_give = (
                prediction.match.phase.bet_points.return_points_result
            )


class TestPredictionsCreateUpdateWithBrowser(PredictionsBaseTestCase):
    def test_create_prediction_form(self):
        for user in self.test_users:
            self.login_user(user=user)
            predictions_url = reverse("create_predictions")
            self.driver.get(f"{self.live_server_url}{predictions_url}")
            self.validate_submit_btn()
            self.validate_user_predictions(user=user, matches=self.mixin.matches)

    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_try_to_create_prediction_for_started_match(self, mocked_datetime):
        mocked_datetime.return_value = timezone.now()
        self.login_user(user=self.test_users[0])
        predictions_url = reverse("create_predictions")
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        submit = self.validate_submit_btn()
        counter = 0
        for match in self.mixin.matches:
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            counter += 1

        match = self.mixin.matches.first()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH - 1
        mocked_datetime.return_value = match.match_start_time - timezone.timedelta(
            minutes=delta_minutes
        )
        submit.send_keys(Keys.RETURN)
        self.assertEqual(self.test_users[0].predictions.all().count(), 0)
        self.validate_404()

    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_create_prediction_some_matches_started(self, mocked_datetime):
        mocked_datetime.return_value = (
            Match.objects.first().match_start_time + timezone.timedelta(minutes=30)
        )
        mixin = GetEventMatchesMixin(event=self.event)
        self.login_user(user=self.test_users[0])
        predictions_url = reverse("create_predictions")
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        self.validate_user_predictions(matches=mixin.matches, user=self.test_users[0])
        self.assertEqual(
            self.test_users[0].predictions.all().count(), mixin.matches.count()
        )
        self.assertNotEqual(
            self.test_users[0].predictions.all().count(), self.mixin.matches.count()
        )

    def test_update_prediction_form(self):
        add_user_predictions(event=self.event, users=0)
        for user in self.test_users:
            self.login_user(user=user)
            for prediction in user.predictions.all():
                if prediction.match not in self.mixin.matches:
                    break
                match = Match.objects.filter(pk=prediction.match.pk)
                predictions_url = reverse(
                    "update_prediction", kwargs={"pk": prediction.pk}
                )
                self.driver.get(f"{self.live_server_url}{predictions_url}")
                self.validate_submit_btn()
                self.validate_user_predictions(user=user, matches=match)

    def test_user_update_prediction_of_other_user(self):
        add_user_predictions(event=self.event, users=0)
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[1].predictions.all().first()
        predictions_url = reverse("update_prediction", kwargs={"pk": prediction.pk})
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        self.validate_404()

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
        predictions_url = reverse("update_prediction", kwargs={"pk": prediction.pk})
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        submit = self.validate_submit_btn()

        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH - 1
        mocked_datetime.return_value = (
            prediction.match.match_start_time
            - timezone.timedelta(minutes=delta_minutes)
        )
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
        self.assertEqual(
            prediction.bet_points.apply_match_state, bet_additional_specs[1]
        )
        self.assertEqual(prediction.bet_points.apply_result, bet_additional_specs[2])
        self.validate_submit_btn(should_have_submit_btn=False)
        self.validate_404()

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
        predictions_url = reverse("update_prediction", kwargs={"pk": prediction.pk})
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        submit = self.validate_submit_btn()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH + 1
        mocked_datetime.return_value = (
            prediction.match.match_start_time
            - timezone.timedelta(minutes=delta_minutes)
        )
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

    def test_invalid_form_check(self):
        self.login_user(user=self.test_users[0])
        predictions_url = reverse("create_predictions")
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        wrong_prediction_match = 0
        for match in self.mixin.matches:
            counter = 0
            for match in self.mixin.matches:
                if wrong_prediction_match == counter:
                    prediction_data = create_invalid_prediction()
                    self.fill_in_prediction(
                        form_id=str(counter), prediction=prediction_data
                    )
                else:
                    prediction_data = create_valid_prediction()
                    self.fill_in_prediction(
                        form_id=str(counter), prediction=prediction_data
                    )
                counter += 1

            submit = self.driver.find_elements(By.CSS_SELECTOR, "input[type=submit]")[0]
            submit.send_keys(Keys.RETURN)
            wrong_prediction_match += 1
        self.assertEqual(self.test_users[0].predictions.all().count(), 0)

    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_update_prediction_valid_apply_match_state_initial_value(
        self, mocked_datetime
    ):
        add_user_predictions(event=self.event, users=0)
        self.login_user(user=self.test_users[0])
        prediction = self.test_users[0].predictions.all().first()
        delta_minutes = settings.PREDICTION_MINUTES_BEFORE_MATCH + 1
        mocked_datetime.return_value = (
            prediction.match.match_start_time
            - timezone.timedelta(minutes=delta_minutes)
        )
        predictions_url = reverse("update_prediction", kwargs={"pk": prediction.pk})
        # validate applied
        bet_points_obj = prediction.bet_points
        bet_points_obj.apply_match_state = True
        bet_points_obj.save()
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        checkbox = self.driver.find_element(By.NAME, "form-0-accept_match_state_bet")
        self.assertTrue(checkbox.is_selected())
        # validate not applied
        bet_points_obj = prediction.bet_points
        bet_points_obj.apply_match_state = False
        bet_points_obj.save()
        self.driver.get(f"{self.live_server_url}{predictions_url}")
        checkbox = self.driver.find_element(By.NAME, "form-0-accept_match_state_bet")
        self.assertFalse(checkbox.is_selected())


class TestMenuBannerBrowser(PredictionsBaseTestCase):
    def test_not_logged_in_user_banner(self):
        self.driver.get(self.live_server_url)
        banner = self.driver.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 0)

    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_available_matches_today(self, mocked_datetime):
        mocked_datetime.return_value = (
            Match.objects.all().first().match_start_time
            - timezone.timedelta(minutes=60)
        )
        self.login_user(self.test_users[0])
        self.driver.get(self.live_server_url)
        banner = self.driver.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 1)

    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_gave_predictions(self, mocked_datetime):
        match = Match.objects.all().first()
        user = self.test_users[0]
        mocked_datetime.return_value = match.match_start_time - timezone.timedelta(
            minutes=60
        )
        self.login_user(user)
        self.create_user_prediction(user=user, match=match)
        self.driver.get(self.live_server_url)
        banner = self.driver.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 0)


class TestPredictionCalculator(PredictionsBaseTestCase):
    def check_prediction_points(self, user):
        points = 0
        for match in Match.objects.all():
            user_prediction, bet_points = self.create_user_prediction(user, match)
            chosen_method = random.choice(list(self._generate_methods.keys()))
            klass_method = getattr(self, chosen_method)
            points_gained = klass_method(user_prediction=user_prediction)
            points += points_gained
            # score tests
            user_score = UserScore.objects.get(user=user)
            self.assertEqual(user_score.points, points)
            prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
            self.assertEqual(prediction_obj.points_gained, points_gained)
            self.assertEqual(
                prediction_obj.points_gained,
                (prediction_obj.base_points + prediction_obj.additional_points),
            )

    def test_base_user_prediction_points(self):
        for user in self.test_users:
            self.check_prediction_points(user=user)

    def test_apply_match_state_bet_nothing_guessed(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_match_state=True
        )
        points = self.generate_match_prediction_nothing_guessed(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(
            user_score.points, points - bet_points.points_match_state_to_take
        )
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, 0 - bet_points.points_match_state_to_take
        )
        self.assertEqual(
            prediction_obj.points_gained, points - bet_points.points_match_state_to_take
        )

    def test_apply_match_state_bet_guessed_state(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_match_state=True
        )
        points = self.generate_match_prediction_guessed_state(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(
            user_score.points, points + bet_points.points_match_state_to_give
        )
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, bet_points.points_match_state_to_give
        )
        self.assertEqual(
            prediction_obj.points_gained, points + bet_points.points_match_state_to_give
        )

    def test_apply_match_state_bet_guessed_result(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_match_state=True
        )
        points = self.generate_match_prediction_guessed_result(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(
            user_score.points, points + bet_points.points_match_state_to_give
        )
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, bet_points.points_match_state_to_give
        )
        self.assertEqual(
            prediction_obj.points_gained, points + bet_points.points_match_state_to_give
        )

    def test_apply_result_bet_nothing_guessed(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_result=True
        )
        points = self.generate_match_prediction_nothing_guessed(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points - bet_points.points_result_to_take)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, 0 - bet_points.points_result_to_take
        )
        self.assertEqual(
            prediction_obj.points_gained, points - bet_points.points_result_to_take
        )

    def test_apply_result_bet_guessed_state(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_result=True
        )
        points = self.generate_match_prediction_guessed_state(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points - bet_points.points_result_to_take)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, 0 - bet_points.points_result_to_take
        )
        self.assertEqual(
            prediction_obj.points_gained, points - bet_points.points_result_to_take
        )

    def test_apply_result_bet_guessed_result(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(
            user, match, apply_result=True
        )
        points = self.generate_match_prediction_guessed_result(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points + bet_points.points_result_to_give)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(
            prediction_obj.additional_points, bet_points.points_result_to_give
        )
        self.assertEqual(
            prediction_obj.points_gained, points + bet_points.points_result_to_give
        )


class TestCalculateExtraBetPointsBalance(PredictionsBaseTestCase):
    def test_random_calculate_extra_bet_points(self):
        counter = 0
        for user in self.test_users:
            points_gained = 0
            for match in Match.objects.all():
                user_prediction, bet_points = self.create_user_prediction(
                    user,
                    match,
                    apply_result=random.choice([True, False]),
                    apply_match_state=random.choice([True, False]),
                )
                chosen_method = random.choice(list(self._generate_methods.keys()))
                klass_method = getattr(self, chosen_method)
                temp_points_gained = klass_method(
                    user_prediction=user_prediction, base_points_only=False
                )
                points_gained += temp_points_gained
                # actual tests
                user_score = UserScore.objects.get(user=user)
                self.assertEqual(user_score.points, points_gained)
                prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
                self.assertEqual(prediction_obj.points_gained, temp_points_gained)
                self.assertEqual(
                    prediction_obj.points_gained,
                    prediction_obj.base_points + prediction_obj.additional_points,
                )
                counter += 1
        logger.info(
            "Passed < test_random_calculate_extra_bet_points >  %s times", str(counter)
        )
