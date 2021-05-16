from django.contrib import admin
from bonus_points.models import BonusDescription, BonusUserPrediction, UserBonusSummary, BonusUserAutoPoints

# Register your models here.
admin.site.register(BonusDescription)
admin.site.register(BonusUserPrediction)
admin.site.register(UserBonusSummary)
admin.site.register(BonusUserAutoPoints)