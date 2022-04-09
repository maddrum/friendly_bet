from django.contrib import admin

from matches.models import Match, MatchResult


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class MatchAdmin(ReadOnlyFields):
    readonly_fields = ('created_on', 'edited_on')
    search_fields = ('home__name', 'guest__name', 'match_number')
    autocomplete_fields = ('home', 'guest')
    list_display = ('home', 'guest', 'match_number', 'match_start_time')


admin.site.register(Match, MatchAdmin)
admin.site.register(MatchResult, ReadOnlyFields)
