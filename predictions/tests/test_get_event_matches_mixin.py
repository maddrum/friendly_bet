from django.test import TestCase

from predictions.views_mixins import GetEventMatchesMixin


class TestEventMatchesMixin(TestCase):
    def test_no_matches_available(self):
        mixin = GetEventMatchesMixin()
        self.assertFalse(mixin.matches.exists())
        self.assertIsNone(mixin.event)
        self.assertIsNone(mixin.all_today_matches)

    # todo add more
