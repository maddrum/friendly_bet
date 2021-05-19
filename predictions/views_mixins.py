import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls.exceptions import Http404
from django.utils import timezone
from django.views.generic import ListView, TemplateView
from extra_views import ModelFormSetView

from accounts.models import LastUserMatchInputStart
from events.models import Event
from matches.models import Matches
from predictions.forms import PredictionForm
from predictions.formsets import PredictionFormSet
# from bonus_points.models import UserBonusSummary
from predictions.models import UserPredictions
from predictions.models import UserScores


class GetEventMatchesMixin:
    event = None
    matches = None
    all_today_matches = None

    def __init__(self, event=None):
        self.event = event
        self._get_event()
        self.get_current_matches()

    def _get_event(self):
        if self.event is None:
            self.event = Event.objects.all().first()

    def _get_event_start_wrap(self):
        return datetime.datetime.combine(self.event.event_start_date, datetime.time(23, 59, 59))

    def _get_now_plus_time(self, plus_minutes=15):
        now_time = timezone.now()

        # todo debug remove
        now_time = datetime.datetime(2021, 6, 16, 21, 44)

        return now_time + datetime.timedelta(minutes=plus_minutes)

    def _get_first_match_start_time(self):
        qs = self.matches.order_by('match_start_time')
        return qs.first().match_start_time - datetime.timedelta(minutes=1)

    def get_current_matches(self):
        now_plus_time = self._get_now_plus_time()
        event_start = self._get_event_start_wrap()
        if now_plus_time < event_start:
            self.matches = Matches.objects.filter(phase__event=self.event, match_start_time__lte=event_start)
            self.all_today_matches = self.matches
        else:
            start_time = datetime.datetime.combine(now_plus_time.date(), datetime.time(0, 0, 1))
            final_time = datetime.datetime.combine(now_plus_time.date(), datetime.time(23, 59, 59))
            self.all_today_matches = Matches.objects.filter(phase__event=self.event, match_start_time__gte=start_time,
                                                            match_start_time__lte=final_time)
            self.matches = self.all_today_matches.filter(match_start_time__gte=now_plus_time)
        self.matches = self.matches.order_by('match_number')
