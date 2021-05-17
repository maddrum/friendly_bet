from django.contrib import admin
from events.models import Event, EventPhases, EventGroups, EventMatchStates, Teams


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class EventPhasesAdmin(ReadOnlyFields):
    obj = None

    def get_object(self, request, object_id, from_field=None):
        self.obj = super().get_object(request, object_id, from_field=None)
        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if type(db_field.related_model) == type(EventMatchStates):
            qs = field.queryset
            field.queryset = qs.filter(event=self.obj.event)

        return field


admin.site.register(Event, ReadOnlyFields)
admin.site.register(EventPhases, EventPhasesAdmin)
admin.site.register(EventGroups, ReadOnlyFields)
admin.site.register(EventMatchStates, ReadOnlyFields)
admin.site.register(Teams, ReadOnlyFields)
