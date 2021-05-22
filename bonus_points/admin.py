from django.contrib import admin
from bonus_points.models import BonusDescription, BonusUserPrediction, BonusUserScore, UserBonusSummary


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


admin.site.register(BonusDescription, ReadOnlyFields)
admin.site.register(BonusUserPrediction, ReadOnlyFields)
admin.site.register(BonusUserScore, ReadOnlyFields)
admin.site.register(UserBonusSummary, ReadOnlyFields)
