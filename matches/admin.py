from django.contrib import admin
from matches.models import Countries, Matches, UserPredictions, UserScore, EventDates

admin.site.register(Countries)
admin.site.register(Matches)
admin.site.register(UserPredictions)
admin.site.register(UserScore)
admin.site.register(EventDates)
