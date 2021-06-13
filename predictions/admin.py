from django.contrib import admin

from predictions.models import UserPredictions, PredictionPoints, UserScores


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class UserPredictionsAdmin(ReadOnlyFields):
    list_display = (
        'user', 'match', 'match_state_guess', 'goals_home', 'goals_home', 'valid_prediction', 'guessed_match_state',
        'guessed_goals_home', 'guessed_goals_guest', 'points_gained')

    def match_state_guess(self, obj):
        return obj.match_state.get_match_state_display()

    def valid_prediction(self, obj):
        return obj.edited_on < obj.match.match_start_time

    valid_prediction.boolean = True

    def guessed_match_state(self, obj):
        return obj.match_state == obj.match.match_result.match_state

    guessed_match_state.boolean = True

    def guessed_goals_home(self, obj):
        if obj.match.match_result.penalties:
            return obj.goals_home == obj.match.match_result.score_after_penalties_home
        return obj.goals_home == obj.match.match_result.score_home

    guessed_goals_home.boolean = True

    def guessed_goals_guest(self, obj):
        if obj.match.match_result.penalties:
            return obj.goals_guest == obj.match.match_result.score_after_penalties_guest
        return obj.goals_guest == obj.match.match_result.score_guest

    guessed_goals_guest.boolean = True

    @admin.display(ordering='prediction_points')
    def points_gained(self, obj):
        return obj.prediction_points.points_gained


admin.site.register(UserPredictions, UserPredictionsAdmin)
admin.site.register(PredictionPoints, ReadOnlyFields)
admin.site.register(UserScores, ReadOnlyFields)
