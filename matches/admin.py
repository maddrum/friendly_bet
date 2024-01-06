from django.contrib import admin

from matches.models import Match, MatchResult


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ("created_on", "edited_on")


class MatchAdmin(ReadOnlyFields):
    readonly_fields = ("created_on", "edited_on")
    search_fields = ("home__name", "guest__name", "match_number")
    autocomplete_fields = ("home", "guest")
    list_display = ("home", "guest", "match_number", "match_start_time")


class MatchResultAdmin(ReadOnlyFields):
    readonly_fields = ("created_on", "edited_on")
    list_display = (
        "match",
        "match_is_over",
        "match_state",
        "score_home",
        "score_guest",
        "penalties",
        "score_after_penalties_home",
        "score_after_penalties_guest",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("match",)
        return super().get_readonly_fields(request=request, obj=obj)

    def render_change_form(self, request, context, *args, **kwargs):
        if context["adminform"].form.instance.pk is None:
            context["adminform"].form.fields["match"].queryset = (
                Match.objects.all()
                .exclude(match_result__match_is_over=True)
                .order_by("match_start_time")
            )
        return super().render_change_form(request, context, *args, **kwargs)


admin.site.register(Match, MatchAdmin)
admin.site.register(MatchResult, MatchResultAdmin)
