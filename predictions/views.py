import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import UpdateView, ListView
from extra_views import ModelFormSetView

from events.models import Event, EventMatchStates
from matches.models import Matches
from predictions.forms import PredictionForm
# from bonus_points.models import UserBonusSummary
from predictions.models import UserPredictions
from predictions.models import UserScores


class RankList(ListView):
    template_name = 'main_app/ranklist.html'
    model = UserScores
    context_object_name = 'ranklist'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-points')
        return queryset


# class RankilstUserPoints(ListView):
#     model = UserPredictions
#     template_name = 'main_app/ranklist-detail.html'
#     context_object_name = 'ranklist'
#
#     def get_queryset(self):
#         user_id = int(self.kwargs['pk'])
#         self.username = get_user_model().objects.get(id=user_id)
#         queryset = UserPredictions.objects.filter(user_id=user_id, match__match_is_over=True).order_by(
#             '-match__match_start_time_utc')
#         return queryset
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data()
#         bonuses_added_check = UserScore.objects.get(user_id=self.username).bonus_points_added
#         if bonuses_added_check:
#             bonuses = UserBonusSummary.objects.get(user=self.username)
#         else:
#             bonuses = False
#         context['bonuses'] = bonuses
#         context['username'] = self.username
#         return context


class EventCreatePredictionView(LoginRequiredMixin, ModelFormSetView):
    template_name = 'predictions/input-prediction.html'
    fields = ('match_state', 'goals_home', 'goals_guest')
    model = UserPredictions
    form_class = PredictionForm
    event = None
    matches = None
    match_states = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = self.get_event()
        self.get_matches()
        self.get_event_match_states()

    def get_event(self):
        return Event.objects.all().first()

    def get_matches(self):
        if self.matches is not None:
            return
        now_time = datetime.datetime.now() + datetime.timedelta(minutes=15)

        # todo debug remove
        now_time = datetime.datetime(2021, 6, 12, 15, 46)
        now_time = now_time + datetime.timedelta(minutes=15)

        event_start = datetime.datetime.combine(self.event.event_start_date, datetime.time(23, 59, 59))

        if now_time < event_start:
            self.matches = Matches.objects.filter(phase__event=self.event, match_start_time__lte=event_start)
        else:
            final_time = datetime.datetime.combine(now_time.date(), datetime.time(23, 59, 59))
            self.matches = Matches.objects.filter(phase__event=self.event, match_start_time__gte=now_time,
                                                  match_start_time__lte=final_time)
        self.matches = self.matches.order_by('match_number')

    def get_queryset(self):
        return UserPredictions.objects.none()

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        kwargs['extra'] = self.matches.count()
        return kwargs

    def get_event_match_states(self):
        if self.match_states is not None:
            return
        self.match_states = EventMatchStates.objects.filter(event=self.event)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        formset = context['formset']
        context['matches'] = list(self.matches)
        index = 0
        for form in formset:
            match = context['matches'][index]
            all_phases = list(match.phase.phase_match_states.all())
            form.fields['match_state'].queryset = self.match_states
        context['formset'] = formset

        return context


class UserUpdatePredictionView(LoginRequiredMixin, UpdateView):
    model = UserPredictions
    template_name = 'accounts/profile-update-match.html'
    context_object_name = 'update_match'
    form_class = PredictionForm

    def get_queryset(self):
        username = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(user_id__username=username)
        return queryset

    def form_valid(self, form):
        show_back_button = True
        checker = False
        post_data = dict(self.request.POST)
        post_data = {key: value for key, value in post_data.items() if key != "csrfmiddlewaretoken"}
        error_text = ''
        tie_statuses = ['tie', 'penalties_home', 'penalties_guest']
        for key in post_data:
            if key == 'prediction_goals_home' or key == 'prediction_goals_guest':
                try:
                    int(post_data[key][0])
                except ValueError:
                    content_dict = {
                        'error_text': 'Моля, въведете цели положителни числа в полетата за гол! Като бройка голове - един, два, три... Опитай пак!',
                    }
                    return render(self.request, 'matches/prediction-error.html', content_dict)
            goals_home = int(post_data['prediction_goals_home'][0])
            goals_guest = int(post_data['prediction_goals_guest'][0])
            if key == 'prediction_match_state':
                if post_data[key][0] == 'home' and goals_home <= goals_guest:
                    checker = True
                    error_text = 'Головете не съотвестват на въведения изход от двубоя. Въведена е победа за домакин, ' \
                                 'но головете на домакина по-малко от тези на госта!'
                elif post_data[key][0] == 'guest' and goals_guest <= goals_home:
                    checker = True
                    error_text = 'Головете не съотвестват на въведения изход от двубоя. Въведена е победа за гост, ' \
                                 'но головете на госта по-малко от тези на домакина!'
                elif post_data[key][0] in tie_statuses and goals_home != goals_guest:
                    checker = True
                    error_text = 'Головете на домакина и на госта не са равни!'

        current_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        match_start_time = self.object.match.match_start_time_utc
        # check for time before applying corrections
        if current_time > match_start_time:
            print(f'NOTE: {self.request.user} tried to change {self.object} at UTC: {current_time}')
            checker = True
            error_text = 'Изтекло време за корекция на прогнозата.'
        if checker:
            content_dict = {
                'error_text': error_text,
                'show_back_button': show_back_button,
            }
            return render(self.request, 'matches/prediction-error.html', content_dict)
        else:
            self.object = form.save(commit=False)
            self.object.last_edit = datetime.datetime.utcnow()
            self.object.save()
            return super().form_valid(form)
