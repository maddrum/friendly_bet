import random

from matches.models import Match
from predictions.models import PredictionPoint, UserScore
from predictions.tests.base import PredictionsBaseTestCase
from utlis.tests.browser_test_utils import handle_failed_browser_test


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

    @handle_failed_browser_test
    def test_base_user_prediction_points(self):
        for user in self.test_users:
            self.check_prediction_points(user=user)

    @handle_failed_browser_test
    def test_apply_match_state_bet_nothing_guessed(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_match_state=True)
        points = self.generate_match_prediction_nothing_guessed(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points - bet_points.points_match_state_to_take)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, 0 - bet_points.points_match_state_to_take)
        self.assertEqual(prediction_obj.points_gained, points - bet_points.points_match_state_to_take)

    @handle_failed_browser_test
    def test_apply_match_state_bet_guessed_state(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_match_state=True)
        points = self.generate_match_prediction_guessed_state(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points + bet_points.points_match_state_to_give)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, bet_points.points_match_state_to_give)
        self.assertEqual(prediction_obj.points_gained, points + bet_points.points_match_state_to_give)

    @handle_failed_browser_test
    def test_apply_match_state_bet_guessed_result(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_match_state=True)
        points = self.generate_match_prediction_guessed_result(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points + bet_points.points_match_state_to_give)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, bet_points.points_match_state_to_give)
        self.assertEqual(prediction_obj.points_gained, points + bet_points.points_match_state_to_give)

    @handle_failed_browser_test
    def test_apply_result_bet_nothing_guessed(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_result=True)
        points = self.generate_match_prediction_nothing_guessed(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points - bet_points.points_result_to_take)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, 0 - bet_points.points_result_to_take)
        self.assertEqual(prediction_obj.points_gained, points - bet_points.points_result_to_take)

    @handle_failed_browser_test
    def test_apply_result_bet_guessed_state(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_result=True)
        points = self.generate_match_prediction_guessed_state(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points - bet_points.points_result_to_take)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, 0 - bet_points.points_result_to_take)
        self.assertEqual(prediction_obj.points_gained, points - bet_points.points_result_to_take)

    @handle_failed_browser_test
    def test_apply_result_bet_guessed_result(self):
        user = self.test_users[0]
        match = self.mixin.matches[0]
        user_prediction, bet_points = self.create_user_prediction(user, match, apply_result=True)
        points = self.generate_match_prediction_guessed_result(user_prediction)
        user_score = UserScore.objects.get(user=user)
        self.assertEqual(user_score.points, points + bet_points.points_result_to_give)
        prediction_obj = PredictionPoint.objects.get(prediction=user_prediction)
        self.assertEqual(prediction_obj.base_points, points)
        self.assertEqual(prediction_obj.additional_points, bet_points.points_result_to_give)
        self.assertEqual(prediction_obj.points_gained, points + bet_points.points_result_to_give)
