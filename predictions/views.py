import datetime
import os
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls.exceptions import Http404
from django.views.generic import ListView, TemplateView
from extra_views import ModelFormSetView

from accounts.models import LastUserMatchInputStart
from bonus_points.models import UserBonusSummary
from predictions.forms import PredictionForm
from predictions.formsets import PredictionFormSet
from predictions.models import BetAdditionalPoint, UserPrediction, UserScore
from predictions.views_mixins import GetEventMatchesMixin


class RankList(ListView):
    template_name = 'predictions/ranklist.html'
    model = UserScore
    context_object_name = 'ranklist'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-points')
        return queryset


class RankilstUserPoints(ListView):
    model = UserPrediction
    template_name = 'main_app/ranklist-detail.html'
    context_object_name = 'ranklist'
    user = None
    paginate_by = 4

    def get_queryset(self):
        self.user = get_user_model().objects.get(pk=self.kwargs['pk'])
        queryset = UserPrediction.objects.filter(
            user=self.user, match__match_result__match_is_over=True).order_by(
            '-match__match_start_time').select_related('match').prefetch_related('match__match_result')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        try:
            bonuses_added_check = UserScore.objects.get(user=self.user).bonus_points_added
        except UserScore.DoesNotExist:
            bonuses_added_check = False
        if bonuses_added_check:
            bonuses = UserBonusSummary.objects.get(user=self.user)
        else:
            bonuses = False
        context['bonuses'] = bonuses
        context['username'] = self.user

        return context


class EventCreatePredictionView(LoginRequiredMixin, GetEventMatchesMixin, ModelFormSetView):
    template_name = 'predictions/input-prediction.html'
    fields = ('match_state', 'goals_home', 'goals_guest')
    model = UserPrediction
    form_class = PredictionForm
    formset_class = PredictionFormSet
    success_url = reverse_lazy('predictions_success')
    user_gave_prediction = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.check_for_user_predictions()
        self.do_initial_checks()
        return super().dispatch(request, *args, **kwargs)

    def do_initial_checks(self):
        if self.request.method == 'POST':
            if self.user_gave_prediction:
                raise Http404()
            if not self.matches.exists():
                raise Http404()
            try:
                user_last_input_start = LastUserMatchInputStart.objects.get(user=self.request.user)
            except LastUserMatchInputStart.DoesNotExist:
                raise Http404()
            if user_last_input_start.valid_to is None:
                raise Http404()
            if self._get_now_plus_time(plus_minutes=0) > user_last_input_start.valid_to:
                raise Http404()

    def check_for_user_predictions(self):
        self.user_gave_prediction = UserPrediction.objects.filter(
            user=self.request.user, match__in=self.all_today_matches).exists()

    def update_form_input_object(self):
        form_check_obj, created = LastUserMatchInputStart.objects.get_or_create(user=self.request.user)
        form_check_obj.valid_to = self._get_first_match_start_time() - datetime.timedelta(
            minutes=settings.PREDICTION_MINUTES_BEFORE_MATCH)
        form_check_obj.save()

    def get_queryset(self):
        return UserPrediction.objects.none()

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

    def get_meme_filenames(self):
        meme_folder = os.path.join(settings.STATIC_ROOT, 'images', 'side_pictures')
        for root, dirs, files in os.walk(meme_folder):
            images = [file for file in files]
            images.sort()
            return images
        return []

    def get_head_img(self):
        images = self.get_meme_filenames()
        meme_index = 0 if 'meme_number' not in self.request.session else self.request.session['meme_number']
        self.request.session['meme_number'] = meme_index + 1 if meme_index < len(images) - 1 else 0
        try:
            image_name = images[meme_index]
        except IndexError:
            self.request.session['meme_number'] = 0
            image_name = images[0]

        picture = f'{settings.STATIC_URL}images/side_pictures/{image_name}'
        return picture

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.update_form_input_object()
        match_check = self.matches.exists()
        if match_check:
            time_delta = self._get_first_match_start_time() - datetime.timedelta(
                minutes=settings.PREDICTION_MINUTES_BEFORE_MATCH)
        else:
            time_delta = False
        if self.user_gave_prediction:
            context['match_check'] = False
        else:
            context['match_check'] = match_check
        context['matches'] = list(self.matches)
        context['time_delta'] = time_delta
        context['head_img'] = self.get_head_img()
        return context

    def update_bet_points(self, form):
        # additional bet points
        add_points_obj, created = BetAdditionalPoint.objects.get_or_create(prediction=form.instance)
        add_points_obj.apply_match_state = form.cleaned_data['accept_match_state_bet']
        add_points_obj.apply_result = form.cleaned_data['accept_match_result_bet']
        phase_points = form.instance.match.phase.bet_points
        add_points_obj.points_match_state_to_take = phase_points.points_state
        add_points_obj.points_match_state_to_give = phase_points.return_points_state
        add_points_obj.points_result_to_take = phase_points.points_result
        add_points_obj.points_result_to_give = phase_points.return_points_result
        add_points_obj.save()

    def formset_valid(self, formset):
        formset_len = len(formset)
        if formset_len != self.matches.count():
            raise Http404()
        index = 0
        for form in formset:
            match = self.matches[index]
            form.instance.match = match
            form.instance.user = self.request.user
            form.save()
            self.update_bet_points(form=form)
            index += 1
        return HttpResponseRedirect(self.get_success_url())


class UserUpdatePredictionView(EventCreatePredictionView):

    def check_for_user_predictions(self):
        self.user_gave_prediction = False

    def get_queryset(self):
        qs = UserPrediction.objects.filter(pk=self.kwargs['pk'])
        obj = qs.first()
        match = obj.match
        self.matches = self.matches.filter(pk=match.pk)
        if not qs.exists() or not self.matches.exists():
            raise Http404()
        if obj.user != self.request.user:
            raise Http404()
        return qs

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        kwargs['extra'] = 0
        return kwargs


class PredictionSuccess(TemplateView):
    template_name = 'predictions/prediction-success.html'
