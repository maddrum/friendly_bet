from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from accounts import forms
from predictions.models import UserPredictions


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
    fields = ('email', 'first_name', 'last_name',)
    template_name = 'accounts/profile-settings.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        username = self.request.user
        queryset = User.objects.get(username=username)
        return queryset


class UserPredictionsListView(LoginRequiredMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-update-predictions.html'
    context_object_name = 'predictions'

    def get_queryset(self):

        queryset = UserPredictions.objects.filter(user=self.request.user)
        return queryset


class ProfilePredictionStats(LoginRequiredMixin, ListView):
    model = UserPredictions
    template_name = 'accounts/profile-history-and-points.html'
    context_object_name = 'history'

    def get_queryset(self):
        queryset = UserPredictions.objects.filter(user=self.request.user)
        return queryset


#
#
# class ProfileBonusView(ListView):
#     model = BonusUserPrediction
#     template_name = 'accounts/profile-bonuses-list.html'
#     context_object_name = 'bonuses'
#
#     def get_queryset(self):
#         username = self.request.user
#         queryset = BonusUserPrediction.objects.filter(user=username)
#         return queryset
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         username = self.request.user
#         context = super().get_context_data()
#         queryset = BonusDescription.objects.filter(participate_link=False, bonus_active=True)
#         queryset_gained_points = BonusUserPrediction.objects.exclude(points_gained=0)
#         queryset_gained_points = queryset_gained_points.filter(user=username)
#         if queryset.count() != 0:
#             context['auto_in'] = queryset
#         else:
#             context['auto_in'] = False
#         if queryset_gained_points.count() != 0:
#             context['points_gained'] = queryset_gained_points
#         else:
#             context['points_gained'] = False
#         queryset_auto_points = BonusUserAutoPoints.objects.filter(user=username)
#         if queryset_auto_points.count() != 0:
#             context['auto_points'] = queryset_auto_points
#         else:
#             context['auto_points'] = False
#         return context


class ProfileLogoutConfirm(TemplateView):
    template_name = 'accounts/logout-confirm.html'
