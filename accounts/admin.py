from django.contrib import admin
from accounts.models import LastUserMatchInputStart, UserExtendModel


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('started_on',)


admin.site.register(LastUserMatchInputStart, ReadOnlyFields)
admin.site.register(UserExtendModel)
