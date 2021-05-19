import datetime

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
    template_name = 'main_app/schedule.html'
    model = Matches
    context_object_name = 'schedule'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        date = datetime.datetime.now()
        all_matches = Matches.objects.all().order_by('phase', 'match_start_time').prefetch_related('match_result')
        # today_matches = Matches.objects.filter(match_date=date)
        # group_phase = Matches.objects.filter(phase='group_phase')
        # eight_finals = Matches.objects.filter(phase='eighth-finals')
        # quarterfinals = Matches.objects.filter(phase='quarterfinals')
        # semifinals = Matches.objects.filter(phase='semifinals')
        # little_final = Matches.objects.filter(phase='little_final')
        # final = Matches.objects.filter(phase='final')
        # context['today_matches'] = today_matches
        # context['group_phase'] = group_phase
        # context['eight_finals'] = eight_finals
        # context['quarterfinals'] = quarterfinals
        # context['semifinals'] = semifinals
        # context['little_final'] = little_final
        # context['final'] = final
        context['matches'] = all_matches
        return context
