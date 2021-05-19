from django.contrib import admin

from predictions.models import UserPredictions


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(UserPredictions, ReadOnlyFields)
