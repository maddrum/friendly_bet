from matches.models import MatchResult
from predictions.models import PredictionPoint, UserPrediction, UserScore
from predictions.prediction_scores import GUESSED_MATCH_RESULT, GUESSED_MATCH_STATE, PARTICIPATION_POINTS


def check_full_score(prediction):
    match_result = prediction.match.match_result
    if prediction.match_state != match_result.match_state:
        return False

    goals_home = match_result.score_after_penalties_home if match_result.penalties else match_result.score_home
    goals_guest = match_result.score_after_penalties_guest if match_result.penalties else match_result.score_guest
    result = prediction.goals_home == goals_home and prediction.goals_guest == goals_guest

    return result


def calculate_user_predictions(instance_id=None):
    if instance_id is None:
        queryset = UserPrediction.objects.filter(match__match_result__isnull=False)
    else:
        try:
            match_result_instance = MatchResult.objects.get(pk=instance_id)
        except MatchResult.DoesNotExist:
            return
        queryset = UserPrediction.objects.filter(match=match_result_instance.match).prefetch_related(
            'match__match_result').select_related('match').select_related('bet_points')

    for prediction in queryset:
        multiplier = prediction.match.phase.multiplier
        points = PARTICIPATION_POINTS
        note = '1. Прогноза за мач: 1 т.'
        # check match state
        if prediction.match_state == prediction.match.match_result.match_state:
            temp_points = GUESSED_MATCH_STATE * multiplier
            points += temp_points
            note = note + f'\n2. Познат изход от срещата: {temp_points} т.'
            if check_full_score(prediction=prediction):
                temp_points = GUESSED_MATCH_RESULT * multiplier
                points += temp_points
                note = note + f'\n3.Познат точен резултат: {temp_points} т.'
        # handle extra bet points
        extra_bet_points, extra_bet_note = calculate_extra_points(prediction)
        note += extra_bet_note
        # update points object
        prediction_points_obj, created = PredictionPoint.objects.get_or_create(prediction=prediction)
        prediction_points_obj.base_points = points
        prediction_points_obj.additional_points = extra_bet_points
        prediction_points_obj.note = note
        prediction_points_obj.save()


def calculate_ranklist(instance_id=None):
    """Calculate the ranklist for match or all matches"""
    if instance_id is None:
        all_predictions = UserPrediction.objects.filter(match__match_result__match_is_over=True).prefetch_related(
            'prediction_points').select_related('match__phase__event')
    else:
        all_predictions = UserPrediction.objects.filter(match__match_result__pk=instance_id).prefetch_related(
            'prediction_points').select_related('match__phase__event')
    if not all_predictions.exists():
        return

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


def calculate_extra_points(prediction):
    result_points = 0
    result_note = ''

    bet_points_obj = prediction.bet_points

    if bet_points_obj.apply_match_state:
        if prediction.match_state == prediction.match.match_result.match_state:
            result_points += bet_points_obj.points_match_state_to_give
            result_note += f'\n Обложи се с джина за изхода от двубоя и взе че позна! ' \
                           f'Джинът ДАДЕ {bet_points_obj.points_match_state_to_give} точки.'
        else:
            result_points -= bet_points_obj.points_match_state_to_take
            result_note += f'\n Обложи се с джина за изхода от двубоя ама удари греда! ' \
                           f'Джинът ВЗЕ {bet_points_obj.points_match_state_to_take} точки от тази "прогноза".'

    if bet_points_obj.apply_result:
        if check_full_score(prediction=bet_points_obj.prediction):
            result_points += bet_points_obj.points_result_to_give
            result_note += f'\n Обложи се с джина за резултата от двубоя и го тресна! ' \
                           f'Джинът ДАДЕ {bet_points_obj.points_result_to_give} точки.'
        else:
            result_points -= bet_points_obj.points_result_to_take
            result_note += f'\n Обложи се с джина за резултата от двубоя ама това беше кур капан! ' \
                           f'Джинът ВЗЕ {bet_points_obj.points_result_to_take} точки от тази "прогноза".'

    return result_points, result_note
