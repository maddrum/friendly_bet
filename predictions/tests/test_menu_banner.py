import logging
from unittest.mock import patch

from django.utils import timezone
from selenium.webdriver.common.by import By

from matches.models import Match
from predictions.tests.base import PredictionsBaseTestCase
from utlis.tests.browser_test_utils import handle_failed_browser_test

logger = logging.getLogger("friendly_bet")
logger.propagate = False


class TestMenuBannerBrowser(PredictionsBaseTestCase):
    @handle_failed_browser_test
    def test_not_logged_in_user_banner(self):
        banner = self.browser.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 0)

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_available_matches_today(self, mocked_datetime):
        mocked_datetime.return_value = Match.objects.all().first().match_start_time - timezone.timedelta(minutes=60)
        self.login_user(self.test_users[0])
        self.load_page(namespace="index")
        banner = self.browser.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 1)

    @handle_failed_browser_test
    @patch("predictions.views_mixins.GetEventMatchesMixin._get_current_time")
    def test_user_gave_predictions(self, mocked_datetime):
        match = Match.objects.all().first()
        user = self.test_users[0]
        mocked_datetime.return_value = match.match_start_time - timezone.timedelta(minutes=60)
        self.login_user(user)
        self.create_user_prediction(user=user, match=match)
        banner = self.browser.find_elements(By.CSS_SELECTOR, ".menu-banner")
        self.assertIsInstance(banner, list)
        self.assertEqual(len(banner), 0)
