from bonus_points.models import AutoBonusUserScore
from predictions.models import UserPredictions

__all__ = ['predictions_for_all', 'prediction_for_first_match']


def predictions_for_all(user, bonus, *args, **kwargs):
    total_match_count = kwargs['total_matches']
    total_user_predictions = UserPredictions.objects.filter(user=user).count()
    if total_match_count == total_user_predictions:
        bonus_obj, created = AutoBonusUserScore.objects.get_or_create(user=user, bonus=bonus)
        bonus_obj.points_gained = bonus.points
        bonus_obj.summary_text = f"Тоз' чукотляк напука прогноза за всеки един мач! " \
                                 f"Еми, заслужи си всичките {bonus.points} точки!"
        bonus_obj.save()
        return f'added {bonus.points} points to user: {user} for bonus: {bonus}'


def prediction_for_first_match(user, bonus, *args, **kwargs):
    first_match = kwargs['first_match']
    check_prediction = UserPredictions.objects.filter(user=user, match=first_match).exists()
    if check_prediction:
        bonus_obj, created = AutoBonusUserScore.objects.get_or_create(user=user, bonus=bonus)
        bonus_obj.points_gained = bonus.points
        bonus_obj.summary_text = f"Тоз' чукотляк напука прогноза за първия мач и взе {bonus.points} точки."
        bonus_obj.save()
        return f'added {bonus.points} points to user: {user} for bonus: {bonus}'
