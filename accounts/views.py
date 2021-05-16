from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts import forms
from matches.models import UserPredictions
from django.contrib.auth.models import User
import datetime
from accounts.forms import UpdatePredictionForm
from bonus_points.models import BonusUserPrediction, BonusDescription, BonusUserAutoPoints


# Create your views here.
class UserRegisterView(CreateView):
    form_class = forms.AccountRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:register_success')


class UserRegisterSuccessView(TemplateView):
    template_name = 'accounts/register-success.html'


class ThankYouView(TemplateView):
    template_name = 'accounts/logout.html'


class UserPredictionsListView(LoginRequiredMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-update-predictions.html'
    context_object_name = 'predictions'

    def get_queryset(self):
        username = self.request.user
        utc_time = datetime.datetime.utcnow()
        utc_time_delta = utc_time + datetime.timedelta(minutes=30)
        queryset = UserPredictions.objects.filter(user_id__username=username,
                                                  match__match_start_time_utc__gte=utc_time_delta)
        return queryset


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


class UserSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('email', 'first_name', 'last_name',)
    template_name = 'accounts/profile-settings.html'
    success_url = '../settings-success'

    def get_object(self, queryset=None):
        username = self.request.user
        queryset = User.objects.get(username=username)
        return queryset


class SettingsSuccess(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile-settings-success.html'


class ProfilePredictionStats(LoginRequiredMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-history-and-points.html'
    context_object_name = 'history'

    def get_queryset(self):
        username = self.request.user
        queryset = UserPredictions.objects.filter(user_id__username=username)
        queryset = queryset.order_by('-match__match_start_time_utc')
        return queryset


class ProfileBonusView(ListView):
    model = BonusUserPrediction
    template_name = 'accounts/profile-bonuses-list.html'
    context_object_name = 'bonuses'

    def get_queryset(self):
        username = self.request.user
        queryset = BonusUserPrediction.objects.filter(user=username)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        username = self.request.user
        context = super().get_context_data()
        queryset = BonusDescription.objects.filter(participate_link=False, bonus_active=True)
        queryset_gained_points = BonusUserPrediction.objects.exclude(points_gained=0)
        queryset_gained_points = queryset_gained_points.filter(user=username)
        if queryset.count() != 0:
            context['auto_in'] = queryset
        else:
            context['auto_in'] = False
        if queryset_gained_points.count() != 0:
            context['points_gained'] = queryset_gained_points
        else:
            context['points_gained'] = False
        queryset_auto_points = BonusUserAutoPoints.objects.filter(user=username)
        if queryset_auto_points.count() != 0:
            context['auto_points'] = queryset_auto_points
        else:
            context['auto_points'] = False
        return context


class ProfileLogoutConfirm(TemplateView):
    template_name = 'accounts/logout-confirm.html'
