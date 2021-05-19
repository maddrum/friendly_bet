from django.contrib import admin
from accounts.models import LastUserMatchInputStart


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('started_on',)


admin.site.register(LastUserMatchInputStart, ReadOnlyFields)
