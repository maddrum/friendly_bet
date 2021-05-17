from django.contrib import admin
from events.models import Event, EventPhases, EventGroups, EventMatchStates, Teams


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(Event, ReadOnlyFields)
admin.site.register(EventPhases, ReadOnlyFields)
admin.site.register(EventGroups, ReadOnlyFields)
admin.site.register(EventMatchStates, ReadOnlyFields)
admin.site.register(Teams, ReadOnlyFields)
