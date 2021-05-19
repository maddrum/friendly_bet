import datetime

from django.utils import timezone
from django.views.generic import ListView

from matches.models import Matches
from predictions.models import UserPredictions


class MatchDetailView(ListView):
    model = UserPredictions
    template_name = 'main_app/match-detail.html'
    context_object_name = 'match'

    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = UserPredictions.objects.filter(match__match_number=pk, match__match_is_over=True).order_by('user_id')
        queryset_match = Matches.objects.filter(match_number=pk)
        for item in queryset_match:
            self.home_team = item.country_home
            self.guest_team = item.country_guest
            self.match_number = item.match_number
            self.match_date = item.match_date
            self.match_time = item.match_start_time
            if item.match_is_over:
                self.score_home = item.score_home
                self.score_guest = item.score_guest
            else:
                self.score_home = '___'
                self.score_guest = '___'
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['home_team'] = self.home_team
        context['guest_team'] = self.guest_team
        context['match_number'] = self.match_number
        context['match_date'] = self.match_date
        context['match_time'] = self.match_time
        context['score_home'] = self.score_home
        context['score_guest'] = self.score_guest
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
