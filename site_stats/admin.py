from django.contrib import admin
from site_stats.models import TotalStats, UserGuessesNumber

admin.site.register(TotalStats)
admin.site.register(UserGuessesNumber)
