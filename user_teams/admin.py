from django.contrib import admin

from user_teams.models import TeamMember, UserTeam


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class ReadOnlyFieldsUUID(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_on', 'edited_on')


admin.site.register(TeamMember, ReadOnlyFields)
admin.site.register(UserTeam, ReadOnlyFieldsUUID)
