import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from extra_views import ModelFormSetView

from events.models import Event
from matches.models import Matches
from predictions.forms import PredictionForm
from predictions.formsets import PredictionFormSet
# from bonus_points.models import UserBonusSummary
from predictions.models import UserPredictions
from predictions.models import UserScores
from django.urls.exceptions import Http404
from accounts.models import LastUserMatchInputStart


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
    formset_class = PredictionFormSet
    success_url = reverse_lazy('profile')
    event = None
    matches = None
    all_today_matches = None
    match_states = None
    user_gave_prediction = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.event = self.get_event()
        self.get_matches()
        if self.request.method == 'POST' and not self.matches.exists():
            print(f'[INFO] Possible cheater: {self.request.user}')
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_event(self):
        return Event.objects.all().first()

    def get_event_start_wrap(self):
        return datetime.datetime.combine(self.event.event_start_date, datetime.time(23, 59, 59))

    def get_matches(self):
        now_time = datetime.datetime.now() + datetime.timedelta(minutes=15)

        # todo debug remove
        now_time = datetime.datetime(2021, 6, 16, 18, 46)
        now_time = now_time + datetime.timedelta(minutes=15)

        event_start = self.get_event_start_wrap()
        if now_time < event_start:
            self.matches = Matches.objects.filter(phase__event=self.event, match_start_time__lte=event_start)
            self.all_today_matches = self.matches
        else:
            start_time = datetime.datetime.combine(now_time.date(), datetime.time(0, 0, 1))
            final_time = datetime.datetime.combine(now_time.date(), datetime.time(23, 59, 59))
            self.all_today_matches = Matches.objects.filter(phase__event=self.event, match_start_time__gte=start_time,
                                                            match_start_time__lte=final_time)
            self.matches = self.all_today_matches.filter(match_start_time__gte=now_time)
        self.matches = self.matches.order_by('match_number')

    def check_for_user_predictions(self):
        now_time = datetime.datetime.now() + datetime.timedelta(minutes=15)

        # todo debug remove
        now_time = datetime.datetime(2021, 6, 16, 12, 46)
        now_time = now_time + datetime.timedelta(minutes=15)

        event_start = self.get_event_start_wrap()
        if now_time < event_start:
            interval_start = datetime.datetime.combine(self.event.event_start_date, datetime.time(0, 0, 1))
            interval_end = datetime.datetime.combine(self.event.event_start_date, datetime.time(23, 59, 59))
        else:
            interval_start = datetime.datetime.combine(now_time.date(), datetime.time(0, 0, 1))
            interval_end = datetime.datetime.combine(now_time.date(), datetime.time(23, 59, 59))

        check = UserPredictions.objects.filter(user=self.request.user, match__match_start_time__gte=interval_start,
                                               match__match_start_time__lte=interval_end).exists()
        return check

    def get_queryset(self):
        return UserPredictions.objects.none()

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        if self.check_for_user_predictions():
            kwargs['extra'] = 0
        else:
            kwargs['extra'] = self.matches.count()
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['matches'] = self.matches
        return kwargs

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)
        context['matches'] = list(self.matches)
        return context

    def formset_valid(self, formset):
        if UserPredictions.objects.filter(user=self.request.user, match__in=self.all_today_matches).exists():
            raise Http404('predictions are available for one of the matches')
        objects = formset.save(commit=False)
        index = 0
        for object in objects:
            match = self.matches[index]
            object.match = match
            object.user = self.request.user
            object.save()
            index += 1
        return HttpResponseRedirect(self.get_success_url())


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
