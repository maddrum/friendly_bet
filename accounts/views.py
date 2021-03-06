from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from accounts import forms
from predictions.models import UserPredictions
from predictions.views_mixins import GetEventMatchesMixin
from django.db.models import Q


class UserRegisterView(CreateView):
    form_class = forms.AccountRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('register_success')


class UserRegisterSuccessView(TemplateView):
    template_name = 'accounts/register-success.html'


class ThankYouView(TemplateView):
    template_name = 'accounts/logout.html'


class UserSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name',)
    template_name = 'accounts/profile-settings.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        username = self.request.user
        queryset = User.objects.get(username=username)
        return queryset


class UserPredictionsListView(LoginRequiredMixin, GetEventMatchesMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-update-predictions.html'
    context_object_name = 'predictions'

    def get_queryset(self):
        current_matches = list(self.matches)
        queryset = UserPredictions.objects.filter(user=self.request.user, match__in=current_matches)
        return queryset


class ProfilePredictionStats(LoginRequiredMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-history-and-points.html'
    context_object_name = 'history'
    paginate_by = 4

    def get_queryset(self):
        queryset = UserPredictions.objects.filter(user=self.request.user).order_by(
            '-match__match_start_time')
        return queryset


class ProfileLogoutConfirm(TemplateView):
    template_name = 'accounts/logout-confirm.html'
