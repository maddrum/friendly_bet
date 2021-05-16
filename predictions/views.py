import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import UpdateView, ListView

from predictions.forms import UpdatePredictionForm
from bonus_points.models import UserBonusSummary
from matches.models import UserPredictions


class RankList(ListView):
    template_name = 'main_app/ranklist.html'
    model = UserScore
    context_object_name = 'ranklist'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-points')
        return queryset


class RankilstUserPoints(ListView):
    model = UserPredictions
    template_name = 'main_app/ranklist-detail.html'
    context_object_name = 'ranklist'

    def get_queryset(self):
        user_id = int(self.kwargs['pk'])
        self.username = get_user_model().objects.get(id=user_id)
        queryset = UserPredictions.objects.filter(user_id=user_id, match__match_is_over=True).order_by(
            '-match__match_start_time_utc')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        bonuses_added_check = UserScore.objects.get(user_id=self.username).bonus_points_added
        if bonuses_added_check:
            bonuses = UserBonusSummary.objects.get(user=self.username)
        else:
            bonuses = False
        context['bonuses'] = bonuses
        context['username'] = self.username
        return context


class UserUpdatePredictionView(LoginRequiredMixin, UpdateView):
    model = UserPredictions
    template_name = 'accounts/profile-update-match.html'
    context_object_name = 'update_match'
    form_class = UpdatePredictionForm

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
