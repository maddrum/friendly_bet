from django.contrib import admin
from matches.models import Matches


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(Matches, ReadOnlyFields)
# admin.site.register(UserPredictions)
# admin.site.register(UserScore)
# admin.site.register(Event)
