import datetime

from django.urls.exceptions import Http404
from django.views.generic import ListView

from matches.models import MatchResult
from matches.models import Matches
from predictions.models import UserPredictions


class MatchDetailView(ListView):
    model = UserPredictions
    template_name = 'matches/match-detail.html'
    context_object_name = 'predictions'
    match = None

    def get_queryset(self):
        try:
            self.match = Matches.objects.get(pk=self.kwargs['pk'])
        except Matches.DoesNotExist:
            raise Http404()
        try:
            match_result = MatchResult.objects.get(match=self.match)
        except MatchResult.DoesNotExist:
            raise Http404()
        if not match_result.match_is_over:
            raise Http404()
        queryset = UserPredictions.objects.filter(match__pk=self.kwargs['pk'],
                                                  match__match_result__match_is_over=True).order_by(
            'user__pk').prefetch_related('match').select_related('match__match_result')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['match'] = self.match

        return context


class ScheduleView(ListView):
    template_name = 'matches/schedule.html'
    model = Matches
    context_object_name = 'schedule'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        current_date = datetime.datetime.now().date()
        # current_date = datetime.date(2021, 6, 16)

        date_bounds = [datetime.datetime.combine(current_date, datetime.time(0, 0, 1)),
                       datetime.datetime.combine(current_date, datetime.time(23, 59, 59))]
        all_matches = Matches.objects.all().order_by('phase', 'match_start_time').prefetch_related('match_result')
        today_matches = all_matches.filter(match_start_time__gte=date_bounds[0], match_start_time__lte=date_bounds[1])
        match_order = {}
        for match in all_matches:
            if match.phase in match_order:
                match_order[match.phase].append(match)
            else:
                match_order[match.phase] = [match]

        context['today_matches'] = today_matches
        context['matches'] = match_order
        return context
