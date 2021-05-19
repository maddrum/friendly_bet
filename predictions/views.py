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
from predictions.views_mixins import GetEventMatchesMixin


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


class EventCreatePredictionView(LoginRequiredMixin, GetEventMatchesMixin, ModelFormSetView):
    template_name = 'predictions/input-prediction.html'
    fields = ('match_state', 'goals_home', 'goals_guest')
    model = UserPredictions
    form_class = PredictionForm
    formset_class = PredictionFormSet
    success_url = reverse_lazy('predictions_success')
    user_gave_prediction = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.check_for_user_predictions()
        self.check_time_state()
        return super().dispatch(request, *args, **kwargs)

    def check_time_state(self):
        if self.request.method == 'POST':
            if self.user_gave_prediction:
                raise Http404()
            try:
                user_last_input_start = LastUserMatchInputStart.objects.get(user=self.request.user)
            except LastUserMatchInputStart.DoesNotExist:
                raise Http404()
            if timezone.now() > user_last_input_start.valid_to:
                raise Http404()

    def check_for_user_predictions(self):
        check = UserPredictions.objects.filter(user=self.request.user, match__in=self.all_today_matches).exists()
        self.user_gave_prediction = check

    def update_form_input_object(self):
        form_check_obj, created = LastUserMatchInputStart.objects.get_or_create(user=self.request.user)
        form_check_obj.valid_to = self._get_first_match_start_time()
        form_check_obj.save()

    def get_queryset(self):
        return UserPredictions.objects.none()

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        if self.user_gave_prediction:
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
        self.update_form_input_object()
        time_delta = self._get_first_match_start_time() - datetime.timedelta(minutes=2)
        context['matches'] = list(self.matches)
        context['time_delta'] = time_delta
        return context

    def formset_valid(self, formset):
        index = 0
        for form in formset:
            match = self.matches[index]
            form.instance.match = match
            form.instance.user = self.request.user
            form.save()
            index += 1
        return HttpResponseRedirect(self.get_success_url())


class UserUpdatePredictionView(EventCreatePredictionView):

    def user_gave_prediction(self):
        self.user_gave_prediction = False

    def get_queryset(self):
        qs = UserPredictions.objects.filter(pk=self.kwargs['pk'])
        return qs

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        kwargs['extra'] = 0
        return kwargs


class PredictionSuccess(TemplateView):
    template_name = 'predictions/prediction-success.html'
