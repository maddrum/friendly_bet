from matches.models import MatchResult
from predictions.models import PredictionPoints, UserPredictions
from predictions.models import UserScores
from predictions.prediction_scores import PARTICIPATION_POINTS, GUESSED_MATCH_STATE, GUESSED_MATCH_RESULT


def calculate_user_predictions(instance_id=None):
    if instance_id is None:
        queryset = UserPredictions.objects.all()
    else:
        try:
            match_result_instance = MatchResult.objects.get(pk=instance_id)
        except MatchResult.DoesNotExist:
            return
        queryset = UserPredictions.objects.filter(match=match_result_instance.match).prefetch_related(
            'match__match_result').select_related('match')

    for prediction in queryset:
        multiplier = prediction.match.phase.multiplier
        points = PARTICIPATION_POINTS
        note = '1. Прогноза за мач: 1 т.'
        # check match state
        if prediction.match_state == prediction.match.match_result.match_state:
            temp_points = GUESSED_MATCH_STATE * multiplier
            points += temp_points
            note = note + f'\n2. Познат изход от срещата: {temp_points} т.'
        # check match result
        check_full_score = False
        if prediction.match.match_result.penalties:
            if prediction.goals_home == prediction.match.match_result.score_after_penalties_home \
                    and prediction.goals_guest == prediction.match.match_result.score_after_penalties_guest:
                check_full_score = True
        else:
            if prediction.goals_home == prediction.match.match_result.score_home \
                    and prediction.goals_guest == prediction.match.match_result.score_guest:
                check_full_score = True
        # assign points
        if check_full_score:
            temp_points = GUESSED_MATCH_RESULT * multiplier
            points += temp_points
            note = note + f'\n3.Познат точен резултат: {temp_points} т.'

        # update points object
        prediction_points_obj, created = PredictionPoints.objects.get_or_create(prediction=prediction)
        prediction_points_obj.points_gained = points
        prediction_points_obj.note = note
        prediction_points_obj.save()


def calculate_ranklist(instance_id=None):
    """Calculate the ranklist for match or all matches"""
    if instance_id is None:
        all_predictions = UserPredictions.objects.all().prefetch_related('prediction_points').select_related(
            'match__phase__event')
    else:
        try:
            match_result_instance = MatchResult.objects.get(pk=instance_id)
        except MatchResult.DoesNotExist:
            return
        all_predictions = UserPredictions.objects.filter(match=match_result_instance.match).prefetch_related(
            'prediction_points')

    ranklist = {item.user_id: 0 for item in all_predictions}
    ranklist_event = {item.user_id: item.match.phase.event for item in all_predictions}

    for item in all_predictions:
        key = item.user_id
        points = ranklist[key]
        points += item.prediction_points.points_gained
        ranklist[key] = points

    for item in ranklist:
        obj, created = UserScores.objects.get_or_create(user_id=item, event=ranklist_event[item])
        obj.points = ranklist[obj.user.id]
        obj.save()
