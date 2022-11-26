from django.contrib import admin

from predictions.models import BetAdditionalPoint, UserPrediction, PredictionPoint, UserScore


class ReadOnlyFields(admin.ModelAdmin):
    readonly_fields = ('created_on', 'edited_on')


class UserPredictionsAdmin(ReadOnlyFields):
    list_display = (
        'user',
        'match', 'match_state_guess',
        'goals_home', 'goals_guest', 'valid_prediction',
        'guessed_match_state', 'guessed_result', 'points_gained',
        'bet_state', 'bet_result',
    )
    list_filter = ('bet_points__apply_match_state', 'bet_points__apply_result')

    def match_state_guess(self, obj):
        return obj.match_state.get_match_state_display()

    def valid_prediction(self, obj):
        return obj.edited_on < obj.match.match_start_time

    valid_prediction.boolean = True

    def guessed_match_state(self, obj):
        return obj.match_state == obj.match.match_result.match_state

    guessed_match_state.boolean = True

    def guessed_result(self, obj):
        if obj.match.match_result.penalties:
            result_home = obj.goals_home == obj.match.match_result.score_after_penalties_home
        else:
            result_home = obj.goals_home == obj.match.match_result.score_home

        if obj.match.match_result.penalties:
            result_guest = obj.goals_guest == obj.match.match_result.score_after_penalties_guest
        else:
            result_guest = obj.goals_guest == obj.match.match_result.score_guest

        return result_home and result_guest

    guessed_result.boolean = True

    @admin.display(ordering='prediction_points__points_gained')
    def points_gained(self, obj):
        return obj.prediction_points.points_gained

    def bet_state(self, obj):
        return obj.bet_points.apply_match_state

    bet_state.boolean = True

    def bet_result(self, obj):
        return obj.bet_points.apply_result

    bet_result.boolean = True


class BetAdditionalPointAdmin(ReadOnlyFields):
    list_display = (
        'prediction', 'apply_match_state', 'apply_result', 'points_match_state_to_take', 'points_match_state_to_give',
        'points_result_to_take', 'points_result_to_give'
    )


class PredictionPointAdmin(ReadOnlyFields):
    list_display = ('prediction', 'points_gained', 'base_points', 'additional_points', 'note')


admin.site.register(UserPrediction, UserPredictionsAdmin)
admin.site.register(PredictionPoint, PredictionPointAdmin)
admin.site.register(UserScore, ReadOnlyFields)
admin.site.register(BetAdditionalPoint, BetAdditionalPointAdmin)
