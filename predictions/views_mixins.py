import datetime
import typing

from django.conf import settings
from django.utils import timezone

from events.models import Event
from matches.models import Match


class GetEventMatchesMixin:
    def __init__(self, event=None):
        self.event = event
        self.matches = Match.objects.none()
        self.all_today_matches = None
        self._get_event()
        self.get_current_matches()

    def _get_event(self):
        if self.event is None:
            self.event = Event.objects.all().first()

    def _get_event_start_wrap(self) -> typing.Optional["Match"]:
        first_match = Match.objects.filter(phase__event=self.event).order_by("match_start_time").first()
        if first_match is None:
            return None
        return first_match.match_start_time

    @staticmethod
    def _get_current_time():
        return timezone.now()

    def _get_now_plus_time(self, plus_minutes=settings.PREDICTION_MINUTES_BEFORE_MATCH):
        return self._get_current_time() + datetime.timedelta(minutes=plus_minutes)

    def _get_first_match_start_time(self):
        qs = self.matches.order_by("match_start_time")
        if not qs.exists():
            return timezone.now() - datetime.timedelta(minutes=10)
        return qs.first().match_start_time

    def get_current_matches(self) -> None:
        now_plus_time = self._get_now_plus_time()
        event_start = self._get_event_start_wrap()
        if event_start is None:
            return
        check_datetime = event_start if now_plus_time.date() < event_start.date() else now_plus_time

        self.all_today_matches = Match.objects.get_matches_for_date(event=self.event, date=check_datetime)
        self.matches = self.all_today_matches.filter(match_start_time__gte=now_plus_time).order_by("match_start_time")
