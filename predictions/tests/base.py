import random

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from accounts.model_factories import UserFactory
from events.models import EventMatchState
from events.settings import ALL_MATCH_STATES_LIST
from matches.models import MatchResult
from matches.tools import initialize_matches
from predictions.models import BetAdditionalPoint, UserPrediction
from predictions.tools import create_valid_prediction, generate_valid_goals_by_match_state, PredictionDTO
from predictions.views_mixins import GetEventMatchesMixin
from utlis.tests.browser_tests import BrowserTestBase


class UserPredictionsToolBox:
    _generate_methods = {
        "generate_match_prediction_nothing_guessed": "Nothing guessed -> 1 pt",
        "generate_match_prediction_guessed_state": "Guessed state -> 4 pt",
        "generate_match_prediction_guessed_result": "Guessed result -> 9 pt",
    }

    @staticmethod
    def handle_user_prediction_bet_points(user_prediction, guessed_state=False, guessed_result=False):
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
    def create_user_prediction(user, match, apply_result=False, apply_match_state=False):
        match_state = random.choice(ALL_MATCH_STATES_LIST)
        state = EventMatchState.objects.get(match_state=match_state)
        goals_home, goals_guest = generate_valid_goals_by_match_state(match_state=match_state)
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
            match_state = EventMatchState.objects.get(match_state=random.choice(ALL_MATCH_STATES_LIST))
            match_result = MatchResult.objects.create(match=match, match_state=match_state)
        match_result.match_is_over = False
        match_result.save()
        return match_result

    def generate_match_prediction_nothing_guessed(self, user_prediction, base_points_only=True):
        return_points = 1
        state = user_prediction.match_state
        while True:
            other_match_state = random.choice(ALL_MATCH_STATES_LIST)
            other_state = EventMatchState.objects.get(match_state=other_match_state)
            if other_state != state:
                break
        result_goals_home, result_goals_guest = generate_valid_goals_by_match_state(match_state=other_match_state)
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
            return_points += self.handle_user_prediction_bet_points(user_prediction=user_prediction)
        return return_points

    def generate_match_prediction_guessed_state(self, user_prediction, base_points_only=True):
        return_points = 4
        match_result = self.get_match_result_obj(match=user_prediction.match)
        match_result.match_state = user_prediction.match_state
        match_result.score_home = user_prediction.goals_home + 1
        match_result.score_guest = user_prediction.goals_guest
        match_result.match_is_over = True
        match_result.save()
        # extra bet points
        if not base_points_only:
            return_points += self.handle_user_prediction_bet_points(user_prediction=user_prediction, guessed_state=True)
        return return_points

    def generate_match_prediction_guessed_result(self, user_prediction, base_points_only=True):
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


class PredictionsBaseTestCase(UserPredictionsToolBox, BrowserTestBase):
    test_users = None
    event = None
    mixin = None

    def setUp(self) -> None:
        super().setUp()
        self.test_users = []
        for item in range(10):
            temp_user = UserFactory()
            self.test_users.append(temp_user)
        self.event = initialize_matches()
        self.mixin = GetEventMatchesMixin(event=self.event)

    def fill_in_prediction(self, form_id, prediction: PredictionDTO):
        match_state_element = self.browser.find_element(By.ID, f"id_form-{str(form_id)}-match_state")
        match_state_selector = Select(match_state_element)
        match_state_selector.select_by_value(str(prediction.pk))

        home_score_element = self.browser.find_element(By.ID, f"id_form-{str(form_id)}-goals_home")
        home_score_element.clear()
        home_score_element.send_keys(prediction.goals_home)

        guest_score_element = self.browser.find_element(By.ID, f"id_form-{str(form_id)}-goals_guest")
        guest_score_element.clear()
        guest_score_element.send_keys(prediction.goals_guest)

        # clicks on bet points checkboxes until state is right
        checkbox_id = f"id_form-{form_id}-accept_match_state_bet"
        apply_match_state = self.browser.find_element(By.ID, checkbox_id)
        if apply_match_state.is_selected() != prediction.apply_match_state:
            self.browser.execute_script(f'document.querySelector("#{checkbox_id}").click()')

        checkbox_id = f"id_form-{form_id}-accept_match_result_bet"
        apply_result = self.browser.find_element(By.ID, checkbox_id)
        if apply_result.is_selected() != prediction.apply_result:
            self.browser.execute_script(f'document.querySelector("#{checkbox_id}").click()')

    def validate_user_predictions(self, user, matches):
        matches_prediction = {}
        counter = 0
        for match in matches:
            # validate apply initial state
            if not UserPrediction.objects.filter(user=user, match=match).exists():
                checkbox_state = self.browser.find_element(By.NAME, f"form-{counter}-accept_match_state_bet")
                checkbox_result = self.browser.find_element(By.NAME, f"form-{counter}-accept_match_result_bet")
                self.assertFalse(checkbox_state.is_selected())
                self.assertFalse(checkbox_result.is_selected())
            # input prediction is driven by the matches which are ordered like
            # GetEventMatchesMixin. This is simulation of so.
            prediction_data = create_valid_prediction()
            self.fill_in_prediction(form_id=str(counter), prediction=prediction_data)
            matches_prediction[match] = prediction_data
            counter += 1
        submit = self.browser.find_elements(By.CSS_SELECTOR, "input[type=submit]")[0]
        submit.send_keys(Keys.RETURN)

        for match in matches:
            given_prediction = matches_prediction[match]
            prediction_qs = UserPrediction.objects.filter(user=user, match=match)
            self.assertEqual(prediction_qs.count(), 1)
            prediction = prediction_qs.first()
            self.assertEqual(prediction.match_state.match_state, given_prediction.match_state)
            self.assertEqual(prediction.goals_home, given_prediction.goals_home)
            self.assertEqual(prediction.goals_guest, given_prediction.goals_guest)
            bet_points = prediction.bet_points
            self.assertEqual(bet_points.apply_match_state, given_prediction.apply_match_state)
            self.assertEqual(bet_points.apply_result, given_prediction.apply_result)
            bet_points.points_match_state_to_take = prediction.match.phase.bet_points.points_state
            bet_points.points_match_state_to_give = prediction.match.phase.bet_points.return_points_state
            bet_points.points_result_to_take = prediction.match.phase.bet_points.points_result
            bet_points.points_result_to_give = prediction.match.phase.bet_points.return_points_result
