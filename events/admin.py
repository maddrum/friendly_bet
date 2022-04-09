from django.contrib import admin

from events.models import Event, EventGroup, EventMatchState, EventPhase, Team


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class EventPhasesAdmin(ReadOnlyFields):
    obj = None
    search_fields = ['phase_match_states']
    list_display = ('phase', 'event', 'multiplier')

    def get_object(self, request, object_id, from_field=None):
        self.obj = super().get_object(request, object_id, from_field=None)
        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if self.obj is None:
            return field
        if type(db_field.related_model) == type(EventMatchState):
            qs = field.queryset
            field.queryset = qs.filter(event=self.obj.event)

        return field


class TeamAdmin(ReadOnlyFields):
    search_fields = ('name',)


admin.site.register(Event, ReadOnlyFields)
admin.site.register(EventPhase, EventPhasesAdmin)
admin.site.register(EventGroup, ReadOnlyFields)
admin.site.register(EventMatchState, ReadOnlyFields)
admin.site.register(Team, TeamAdmin)
