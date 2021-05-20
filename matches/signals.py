from django.db.models.signals import post_save
from django.dispatch import receiver

from matches.models import MatchResult
from predictions.prediction_calculators import calculate_user_predictions, calculate_ranklist


@receiver(post_save, sender=MatchResult)
def score_calculator(sender, instance, created, *args, **kwargs):
    # check for match is over flag
    if not instance.match_is_over:
        return
    # process data
    calculate_user_predictions(instance_id=instance.pk)
    calculate_ranklist(instance_id=instance.pk)
