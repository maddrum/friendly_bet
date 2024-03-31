import datetime
import random
import time

from freezegun import freeze_time
from selenium.webdriver.common.by import By

from events.models import EventMatchState
from events.settings import (
    MATCH_STATE_GUEST,
    MATCH_STATE_HOME,
    MATCH_STATE_PENALTIES_GUEST,
    MATCH_STATE_PENALTIES_HOME,
    MATCH_STATE_TIE,
)
from matches.models import Match, MatchResult
from matches.tools import initialize_matches
from predictions.tests.base import UserPredictionsToolBox
from utlis.tests.browser_test_utils import handle_failed_browser_test
from utlis.tests.browser_tests import BrowserTestBase
from utlis.tests.mixins import BaseFreezeTimeMixin


class MatchDetailViewTest(BaseFreezeTimeMixin, UserPredictionsToolBox, BrowserTestBase):
    event = None

    def setUp(self):
        super().setUp()
        self.event = initialize_matches()

    @staticmethod
    def create_penalty_result(match, match_state):
        tie_result = random.randint(0, 0)
        score_home = random.randint(1, 10)
        if match_state.match_state == MATCH_STATE_PENALTIES_HOME:
            score_guest = random.randint(0, score_home - 1)
        elif match_state.match_state == MATCH_STATE_PENALTIES_GUEST:
            score_guest = random.randint(score_home + 1, 30)
        else:
            return None
        result = MatchResult.objects.create(
            match=match,
            match_state=match_state,
            match_is_over=False,
            score_home=tie_result,
            score_guest=tie_result,
            penalties=True,
            score_after_penalties_home=score_home,
            score_after_penalties_guest=score_guest,
        )
        return result

    @staticmethod
    def create_no_penalty_result(match, match_state):
        score_home = random.randint(1, 10)
        if match_state.match_state == MATCH_STATE_HOME:
            score_guest = random.randint(0, score_home - 1)
        elif match_state.match_state == MATCH_STATE_GUEST:
            score_guest = random.randint(score_home + 1, 30)
        elif match_state.match_state == MATCH_STATE_TIE:
            score_guest = score_home
        else:
            return None
        result = MatchResult.objects.create(
            match=match,
            match_state=match_state,
            match_is_over=False,
            score_home=score_home,
            score_guest=score_guest,
            penalties=False,
        )
        return result

    def assert_result(self, matches=None, dummy_uuid_selector="dummy--all"):
        self.load_page(namespace="schedule")
        time.sleep(0.5)
        self.move_to_element(element=self.browser.find_element(By.CSS_SELECTOR, "button.accordion"))
        self.action_chain_click(self.browser.find_element(By.CSS_SELECTOR, "button.accordion"))
        time.sleep(0.5)
        _matches = matches if matches else Match.objects.all()
        for match in _matches:
            result = match.match_result if hasattr(match, "match_result") else None
            wrp_el = self.browser.find_element(By.CSS_SELECTOR, f'.{dummy_uuid_selector}[data-uuid="{match.uuid}"]')
            self.move_to_element(element=wrp_el)
            self.assertEqual(f"МАЧ {match.match_number}", wrp_el.find_element(By.CSS_SELECTOR, ".match-number").text)
            self.assertEqual(match.home.name.upper(), wrp_el.find_element(By.CSS_SELECTOR, ".dummy--home-name").text)
            self.assertEqual(match.guest.name.upper(), wrp_el.find_element(By.CSS_SELECTOR, ".dummy--guest-name").text)
            if result and result.match_is_over:
                if result.penalties:
                    _score_home = result.score_after_penalties_home
                    _score_guest = result.score_after_penalties_guest
                else:
                    _score_home = result.score_home
                    _score_guest = result.score_guest
                self.assertEqual(str(_score_home), wrp_el.find_element(By.CSS_SELECTOR, ".dummy--home-score").text)
                self.assertEqual(str(_score_guest), wrp_el.find_element(By.CSS_SELECTOR, ".dummy--guest-score").text)
            else:
                self.assertEqual("⚽", wrp_el.find_element(By.CSS_SELECTOR, ".dummy--home-score").text)
                self.assertEqual("⚽", wrp_el.find_element(By.CSS_SELECTOR, ".dummy--guest-score").text)
            self.assertEqual(
                match.match_start_time.strftime("%d.%m.%Y@%H:%M"),
                wrp_el.find_element(By.CSS_SELECTOR, ".dummy--date").text,
            )
            if result and result.match_is_over and result.penalties:
                self.assertEqual("след дузпи", wrp_el.find_element(By.CSS_SELECTOR, ".dummy--penalties").text.lower())
            else:
                self.assertEqual(0, len(wrp_el.find_elements(By.CSS_SELECTOR, ".dummy--penalties")))

    @handle_failed_browser_test
    def test_get_matches_view_match_has_no_result(self):
        self.assert_result()

    @handle_failed_browser_test
    def test_get_matches_view_match_is_finished_no_penalties(self):
        self.assert_result()
        for match_state in EventMatchState.objects.filter(event=self.event):
            match = Match.objects.filter(match_result__isnull=True).order_by("?").first()
            result = self.create_no_penalty_result(match=match, match_state=match_state)
            if result is None:
                continue
            self.assert_result()
            result.match_is_over = True
            result.save()
            self.assert_result()

    @handle_failed_browser_test
    def test_get_matches_view_match_is_finished_with_penalties(self):
        for match_state in EventMatchState.objects.filter(event=self.event):
            match = Match.objects.filter(match_result__isnull=True).order_by("?").first()
            result = self.create_penalty_result(match=match, match_state=match_state)
            if result is None:
                continue
            self.assert_result()
            result.match_is_over = True
            result.save()
            self.assert_result()

    @handle_failed_browser_test
    def test_today_matches(self):
        self.assert_result()
        self.freezer.stop()
        new_dt = self.to_freeze_datetime + datetime.timedelta(days=3)
        self.freezer = freeze_time(new_dt)
        self.freezer.start()

        self.assert_result()
        matches = Match.objects.get_matches_for_date(new_dt.date())
        self.assert_result(matches=matches, dummy_uuid_selector="dummy--today")
        self.assertEqual("мачовете днес", self.browser.find_element(By.CSS_SELECTOR, "h2").text.lower())

        result_no_penalties = self.create_no_penalty_result(
            match=matches[0], match_state=EventMatchState.objects.get(event=self.event, match_state=MATCH_STATE_TIE)
        )
        result_no_penalties.match_is_over = True
        result_no_penalties.save()

        result_penalties = self.create_penalty_result(
            match=matches[1],
            match_state=EventMatchState.objects.get(event=self.event, match_state=MATCH_STATE_PENALTIES_GUEST),
        )
        result_penalties.match_is_over = True
        result_penalties.save()

        self.assert_result(matches=matches, dummy_uuid_selector="dummy--today")
