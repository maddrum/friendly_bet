from matches.models import MatchResult
from predictions.models import PredictionPoint, UserPrediction, UserScore
from predictions.prediction_scores import GUESSED_MATCH_RESULT, GUESSED_MATCH_STATE, PARTICIPATION_POINTS


def calculate_user_predictions(instance_id=None):
    if instance_id is None:
        queryset = UserPrediction.objects.all()
    else:
        try:
            match_result_instance = MatchResult.objects.get(pk=instance_id)
        except MatchResult.DoesNotExist:
            return
        queryset = UserPrediction.objects.filter(match=match_result_instance.match).prefetch_related(
            'match__match_result').select_related('match').select_related('bet_points')

    for prediction in queryset:
        check_full_score = False
        multiplier = prediction.match.phase.multiplier
        points = PARTICIPATION_POINTS
        note = '1. Прогноза за мач: 1 т.'
        # check match state
        if prediction.match_state == prediction.match.match_result.match_state:

            temp_points = GUESSED_MATCH_STATE * multiplier
            points += temp_points
            note = note + f'\n2. Познат изход от срещата: {temp_points} т.'
            # check match result
            if prediction.match.match_result.penalties:
                check_full_score = prediction.goals_home == prediction.match.match_result.score_after_penalties_home \
                                   and prediction.goals_guest == prediction.match.match_result.score_after_penalties_guest
            else:
                check_full_score = prediction.goals_home == prediction.match.match_result.score_home \
                                   and prediction.goals_guest == prediction.match.match_result.score_guest
            # assign points
            if check_full_score:
                temp_points = GUESSED_MATCH_RESULT * multiplier
                points += temp_points
                note = note + f'\n3.Познат точен резултат: {temp_points} т.'
        # handle extra bet points
        extra_bet_points, extra_bet_note = calculate_extra_points(prediction, check_full_score)
        points += extra_bet_points
        note += extra_bet_note

        # update points object
        prediction_points_obj, created = PredictionPoint.objects.get_or_create(prediction=prediction)
        prediction_points_obj.points_gained = points
        prediction_points_obj.note = note
        prediction_points_obj.save()


def calculate_ranklist(instance_id=None):
    """Calculate the ranklist for match or all matches"""
    if instance_id is None:
        all_predictions = UserPrediction.objects.filter(match__match_result__match_is_over=True).prefetch_related(
            'prediction_points').select_related('match__phase__event')
    else:
        try:
            match_result_instance = MatchResult.objects.get(pk=instance_id)
        except MatchResult.DoesNotExist:
            return
        all_predictions = UserPrediction.objects.filter(match=match_result_instance.match).prefetch_related(
            'prediction_points')

    ranklist = {item.user_id: 0 for item in all_predictions}
    ranklist_event = {item.user_id: item.match.phase.event for item in all_predictions}

    for item in all_predictions:
        key = item.user_id
        points = ranklist[key]
        points += item.prediction_points.points_gained
        ranklist[key] = points

    for item in ranklist:
        obj, created = UserScore.objects.get_or_create(user_id=item, event=ranklist_event[item])
        if instance_id is None:
            obj.points = ranklist[obj.user.id]
        else:
            obj.points += ranklist[obj.user.id]
        obj.save()


def calculate_extra_points(prediction, check_full_score):
    result_points = 0
    result_note = ''

    bet_points_obj = prediction.bet_points

    if bet_points_obj.points_match_state == 0 and bet_points_obj.points_result == 0:
        return result_points, result_note

    if bet_points_obj.points_match_state != 0:
        if prediction.match_state == prediction.match.match_result.match_state:
            add_points = bet_points_obj.multiplier * bet_points_obj.points_match_state
            result_points += add_points
            result_note += f'\n Беше "уредил/а" изхода от двубоя, ' \
                           f'затова от точките си даде: {bet_points_obj.points_match_state}.' \
                           f'И позна та получи още: ' \
                           f'{bet_points_obj.multiplier} * {bet_points_obj.points_match_state} = {add_points} '
        else:
            result_points -= bet_points_obj.points_match_state
            result_note += f'\n Беше "уредил/а" изхода от двубоя, ' \
                           f'затова от точките си даде: {bet_points_obj.points_match_state}.' \
                           f'Ама сделката пропадна и затова ги взехме.'

    if bet_points_obj.points_match_state != 0:
        if check_full_score:
            add_points = bet_points_obj.multiplier * bet_points_obj.points_result
            result_points += add_points
            result_note += f'\n Беше "уредил/а" мача да свърши {prediction.goals_home}:{prediction.goals_guest}, ' \
                           f'затова от точките си даде: {bet_points_obj.points_match_state}.' \
                           f'И позна та получи още: ' \
                           f'{bet_points_obj.multiplier} * {bet_points_obj.points_match_state} = {add_points} '
        else:
            result_points -= bet_points_obj.points_result
            result_note += f'\n Беше "уредил/а" мача да свърши {prediction.goals_home}:{prediction.goals_guest}, ' \
                           f'затова от точките си даде: {bet_points_obj.points_match_state}.' \
                           f'Ама Меси удари гредата и затова ги взехме.'

    return result_points, result_note
