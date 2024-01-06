from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.views.generic import ListView, TemplateView

from matches.models import Match
from predictions.models import PredictionPoint, UserPrediction, UserScore


class RankListView(ListView):
    template_name = "ranklists/ranklist.html"
    model = UserScore
    context_object_name = "ranklist"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by("-points")
        return queryset


class RankilstUserPointsView(ListView):
    model = UserPrediction
    template_name = "ranklists/ranklist-detail.html"
    context_object_name = "ranklist"
    user = None
    paginate_by = 4

    def get_queryset(self):
        self.user = get_user_model().objects.get(pk=self.kwargs["pk"])
        queryset = (
            UserPrediction.objects.filter(user=self.user, match__match_result__match_is_over=True)
            .order_by("-match__match_start_time")
            .select_related("match")
            .prefetch_related("match__match_result")
        )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context["username"] = self.user
        return context


class GinPointsMatchesView(TemplateView):
    template_name = "ranklists/gin/matches.html"

    def get_points_per_match(self):
        raw_data = list(
            PredictionPoint.objects.all()
            .order_by("-prediction__match__match_start_time")
            .values("prediction__match")
            .annotate(Sum("additional_points"))
        )
        result = {
            Match.objects.get(pk=item["prediction__match"]): item["additional_points__sum"] * -1 for item in raw_data
        }
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_balance"] = (
            PredictionPoint.objects.all().aggregate(Sum("additional_points")).get("additional_points__sum") * -1
        )
        context["per_match"] = self.get_points_per_match()

        page_number = self.request.GET.get("page")
        paginator = Paginator(list(self.get_points_per_match().keys()), 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context


class GinPointsUsersView(TemplateView):
    template_name = "ranklists/gin/users.html"

    @staticmethod
    def get_data():
        qs = (
            PredictionPoint.objects.filter(additional_points__lt=0)
            .values("prediction__user")
            .annotate(Sum("additional_points"))
        )
        raw_data = list(qs)
        result_negative = {
            get_user_model().objects.get(pk=item["prediction__user"]): item["additional_points__sum"]
            for item in raw_data
        }

        qs = (
            PredictionPoint.objects.filter(additional_points__gt=0)
            .values("prediction__user")
            .annotate(Sum("additional_points"))
        )
        raw_data = list(qs)
        result_positive = {
            get_user_model().objects.get(pk=item["prediction__user"]): item["additional_points__sum"]
            for item in raw_data
        }

        result = {
            user: result_positive.get(user, 0) + result_negative.get(user, 0) for user in get_user_model().objects.all()
        }
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["per_user"] = self.get_data()
        return context


class GinPointsNumberOfUsagesView(TemplateView):
    template_name = "ranklists/gin/usages.html"

    @staticmethod
    def get_data():
        qs = (
            PredictionPoint.objects.annotate(Count("prediction__bet_points__apply_match_state"))
            .filter(
                prediction__bet_points__apply_match_state=True,
                prediction__bet_points__apply_match_state__count__gt=0,
            )
            .values("prediction__user")
            .annotate(Count("prediction__bet_points__apply_match_state"))
        )
        raw_data = list(qs)
        result_state = {
            get_user_model().objects.get(pk=item["prediction__user"]): item[
                "prediction__bet_points__apply_match_state__count"
            ]
            for item in raw_data
        }

        qs = (
            PredictionPoint.objects.annotate(Count("prediction__bet_points__apply_result"))
            .filter(
                prediction__bet_points__apply_result=True,
                prediction__bet_points__apply_result__count__gt=0,
            )
            .values("prediction__user")
            .annotate(Count("prediction__bet_points__apply_result"))
        )
        raw_data = list(qs)
        result_result = {
            get_user_model().objects.get(pk=item["prediction__user"]): item[
                "prediction__bet_points__apply_result__count"
            ]
            for item in raw_data
        }

        result = {
            user: result_state.get(user, 0) + result_result.get(user, 0)
            for user in get_user_model().objects.all()
            if user in result_result or user in result_state
        }
        result = {item: result[item] for item in sorted(result, key=lambda x: result[x], reverse=True)}
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["per_user"] = self.get_data()
        return context
