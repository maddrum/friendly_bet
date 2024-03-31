import logging
import random

from matches.models import Match
from predictions.models import (
    PredictionPoint,
    UserScore,
)
from predictions.tests.base import PredictionsBaseTestCase
from utlis.tests.browser_test_utils import handle_failed_browser_test

logger = logging.getLogger("friendly_bet")
logger.propagate = False


class TestCalculateExtraBetPointsBalance(PredictionsBaseTestCase):
    @handle_failed_browser_test
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
                temp_points_gained = klass_method(user_prediction=user_prediction, base_points_only=False)
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
        logger.info("Passed < test_random_calculate_extra_bet_points >  %s times", str(counter))
