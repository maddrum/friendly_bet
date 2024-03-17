import datetime

from django.views.generic import ListView

from matches.models import Match


class ScheduleView(ListView):
    template_name = "matches/schedule.html"
    model = Match
    context_object_name = "schedule"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        current_date = datetime.datetime.now().date()

        all_matches = (
            Match.objects.all()
            .order_by("phase", "match_start_time")
            .prefetch_related("phase")
            .select_related("match_result")
        )

        today_matches = (
            Match.objects.get_matches_for_date(date=current_date)
            .prefetch_related("phase")
            .select_related("match_result")
        )
        match_order = {}
        for match in all_matches:
            if not match.phase in match_order:
                match_order[match.phase] = {}

            if match.match_start_time.date() in match_order[match.phase]:
                match_order[match.phase][match.match_start_time.date()].append(match)
            else:
                match_order[match.phase][match.match_start_time.date()] = [match]

        context["today_matches"] = today_matches
        context["matches"] = match_order
        return context
