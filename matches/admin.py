from django.contrib import admin

from matches.models import Matches, MatchResult


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(Matches, ReadOnlyFields)
admin.site.register(MatchResult, ReadOnlyFields)
