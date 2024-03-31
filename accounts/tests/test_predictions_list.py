from django.utils import timezone
from freezegun import freeze_time
from selenium.webdriver.common.by import By

from accounts.model_factories import UserFactory
from matches.tools import initialize_matches
from predictions.models import UserPrediction
from predictions.tools import add_user_predictions
from predictions.views_mixins import GetEventMatchesMixin
from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase
from utlis.tests.mixins import BaseFreezeTimeMixin


class TestPredictionList(BaseFreezeTimeMixin, BrowserTestBase):
    user = None
    event = None

    def setUp(self):
        super().setUp()
        self.event = initialize_matches()
        self.user = UserFactory()
        self.login_user(user=self.user)
        # add some other user
        UserFactory()
        add_user_predictions(event=self.event, users=0)

    def validate_predictions_list(self):
        self.load_page(namespace="profile")
        mixin = GetEventMatchesMixin(event=self.event)
        self.assertEqual(
            mixin.matches.count(), len(self.browser.find_elements(By.CSS_SELECTOR, ".game-single.inprofile"))
        )
        for match in mixin.matches:
            self.load_page(namespace="profile")
            prediction = UserPrediction.objects.get(user=self.user, match=match)
            element = self.browser.find_element(By.CSS_SELECTOR, f".dummy--match-number__{match.match_number}")
            self.assertEqual(
                f"Твоята прогноза за мач {match.match_number}".lower(),
                element.find_element(By.CSS_SELECTOR, ".history-ttl").text.strip().lower(),
            )
            self.assertEqual(
                match.home.name.lower(),
                element.find_element(By.CSS_SELECTOR, ".dummy--home__name").text.strip().lower(),
            )
            self.assertEqual(
                str(prediction.goals_home),
                element.find_element(By.CSS_SELECTOR, ".dummy--home__score").text.strip().lower(),
            )
            self.assertEqual(
                match.guest.name.lower(),
                element.find_element(By.CSS_SELECTOR, ".dummy--guest__name").text.strip().lower(),
            )
            self.assertEqual(
                str(prediction.goals_guest),
                element.find_element(By.CSS_SELECTOR, ".dummy--guest__score").text.strip().lower(),
            )
            self.assertEqual(
                prediction.match_state.get_match_state_display().lower(),
                element.find_element(By.CSS_SELECTOR, ".dummy--match__state").text.strip().lower(),
            )
            # gin points
            if prediction.bet_points.apply_match_state:
                expected = (
                    f"Aко познаеш ИЗХОДА ОТ ДВУБОЯ ТИ ще "
                    f"вземеш {prediction.bet_points.points_match_state_to_give} точки. "
                    f"В противен случай АНГЕЛ-А ще ти "
                    f"вземе {prediction.bet_points.points_match_state_to_take} точки."
                )
            else:
                expected = "Нямаш облог с АНГЕЛ-А за ИЗХОДА ОТ ДВУБОЯ"
            self.assertEqual(
                expected.lower(),
                element.find_element(By.CSS_SELECTOR, ".dummy--bet__apply").text.strip().replace("\n", " ").lower(),
            )
            if prediction.bet_points.apply_result:
                expected = (
                    f"Aко познаеш КРАЙНИЯ РЕЗУЛТАТ ТИ ще "
                    f"вземеш {prediction.bet_points.points_result_to_give} точки. "
                    f"В противен случай АНГЕЛ-А ще ти "
                    f"вземе {prediction.bet_points.points_result_to_take} точки."
                )
            else:
                expected = "Нямаш облог с АНГЕЛ-А за КРАЙНИЯ РЕЗУЛТАТ"
            self.assertEqual(
                expected.lower(),
                element.find_element(By.CSS_SELECTOR, ".dummy--bet__result").text.strip().replace("\n", " ").lower(),
            )
            # validate edit button
            href = element.find_element(By.CSS_SELECTOR, f".dummy--submit__{prediction.pk}")
            self.assertEqual(
                self.get_full_url(namespace="update_prediction", reverse_kwargs={"pk": prediction.pk}),
                href.get_attribute("href"),
            )

    @handle_failed_browser_test
    def test_must_be_logged_in(self):
        self.logout_user()
        self.load_page(namespace="profile")
        self.assert_on_login_page()

    @handle_failed_browser_test
    def test_list_is_correct(self):
        self.validate_predictions_list()

    @handle_failed_browser_test
    def test_list_is_correct_shift_dates(self):
        for day in range((self.event.event_end_date - self.event.event_start_date).days):
            self.freezer.stop()
            self.freezer = freeze_time(self.to_freeze_datetime + timezone.timedelta(days=1))
            self.freezer.start()
            self.validate_predictions_list()

    @handle_failed_browser_test
    def test_list_is_correct_shift_hours(self):
        matches = list(GetEventMatchesMixin(event=self.event).matches)
        for match in matches:
            self.freezer.stop()
            self.freezer = freeze_time(match.match_start_time)
            self.freezer.start()
            self.validate_predictions_list()

    def test_no_predictions(self):
        UserPrediction.objects.all().delete()
        self.load_page(namespace="profile")
        self.assertEqual(0, len(self.browser.find_elements(By.CSS_SELECTOR, ".game-single.inprofile")))
