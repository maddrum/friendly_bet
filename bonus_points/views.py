from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.urls.exceptions import Http404
from django.utils import timezone
from django.views.generic import FormView, ListView

from bonus_points.forms import InputAllTeamsForm, InputChoicesForm, InputNumberForm
from bonus_points.models import BonusDescription, BonusUserPrediction
from bonus_points.settings import (
    INPUT_CHOICES_VALUE,
    INPUT_NUMBER_VALUE,
    INPUT_TEAMS_VALUE,
    LAST_BONUS_VISIT_TIME_KEY,
)


class BonusMainListView(LoginRequiredMixin, ListView):
    template_name = "bonus_points/bonus-main.html"
    context_object_name = "bonuses"

    def get_queryset(self):
        queryset = BonusDescription.objects.filter(bonus_active=True)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        self.request.session[LAST_BONUS_VISIT_TIME_KEY] = timezone.now().isoformat()
        context = super().get_context_data()
        queryset = BonusDescription.objects.all()
        current_time = timezone.now()
        active = queryset.filter(active_until__gt=current_time)
        not_active = queryset.filter(active_until__lte=current_time)
        context["active"] = active
        context["not_active"] = not_active
        all_user_predictions = BonusUserPrediction.objects.filter(
            user=self.request.user
        )
        context["all_predictions"] = {
            prediction.bonus: prediction.user_prediction
            for prediction in all_user_predictions
        }
        context["all_user_bonuses"] = [
            prediction.bonus for prediction in list(all_user_predictions)
        ]
        return context


class BonusParticipateView(LoginRequiredMixin, FormView):
    template_name = "bonus_points/bonus-input-form.html"
    bonus = None
    success_url = reverse_lazy("bonus_main")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.get_bonus()
        if request.method == "POST" and timezone.now() > self.bonus.active_until:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_bonus(self):
        try:
            self.bonus = BonusDescription.objects.get(pk=self.kwargs["pk"])
        except BonusDescription.DoesNotExist:
            raise Http404()

    def get_form_class(self):
        form_class = None
        if self.bonus.bonus_input == INPUT_TEAMS_VALUE:
            form_class = InputAllTeamsForm
        if self.bonus.bonus_input == INPUT_CHOICES_VALUE:
            form_class = InputChoicesForm
        if self.bonus.bonus_input == INPUT_NUMBER_VALUE:
            form_class = InputNumberForm
        if form_class is None:
            raise Http404("No form")
        return form_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bonus_obj"] = self.bonus
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.bonus.bonus_input == INPUT_CHOICES_VALUE:
            choices = self.bonus.available_choices.split(",")
            kwargs["choices"] = choices
        return kwargs

    def form_valid(self, form):
        user_prediction = form.cleaned_data["user_prediction"]
        if BonusUserPrediction.objects.filter(
            user=self.request.user, bonus=self.bonus
        ).exists():
            raise Http404()
        prediction_obj = BonusUserPrediction(
            user=self.request.user, bonus=self.bonus, user_prediction=user_prediction
        )
        prediction_obj.save()
        return super().form_valid(form)
