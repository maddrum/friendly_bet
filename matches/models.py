from django.db import models

from events.models import Event, EventPhases, EventGroups, EventMatchStates, Teams


class Matches(models.Model):
    country_home = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='country_home')
    country_guest = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='country_guest')
    phase = models.ForeignKey(EventPhases, on_delete=models.PROTECT, related_name='match_phase')
    match_number = models.IntegerField()
    match_start_time = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return_str = 'мач ' + str(self.match_number) + ' | ' + str(self.country_home) + ' - ' + str(self.country_guest)
        return return_str

    class Meta:
        unique_together = ('country_home', 'country_guest', 'phase',)


class MatchResult(models.Model):
    match = models.OneToOneField(Matches, on_delete=models.CASCADE, related_name='match_result')
    match_state = models.ForeignKey(EventMatchStates, on_delete=models.PROTECT)
    score_home = models.IntegerField(default=0)
    score_guest = models.IntegerField(default=0)
    score_after_penalties_home = models.IntegerField(default=0)
    score_after_penalties_guest = models.IntegerField(default=0)
    penalties = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

# def score_calculator(sender, instance, created, *args, **kwargs):
#     # 1. Calculate points for every user upon saving match result.
#     # 2. Calculate ranklist after every match
#     # check for match_is_over to be true to continue
#     if not instance.match_is_over:
#         return
#     queryset = UserPredictions.objects.filter(match=instance.id)
#     match_goals_home = instance.score_home
#     match_goals_guest = instance.score_guest
#     match_state = instance.match_state
#     # multipliers for quater, semi and finals
#     multiplier_definition = {
#         'group_phase': 1,
#         'eighth-finals': 1,
#         'quarterfinals': 2,
#         'semifinals': 3,
#         'little_final': 3,
#         'final': 4,
#     }
#     multiplier = multiplier_definition[instance.phase]
#
#     for item in queryset:
#         user_prediction_goals_home = item.prediction_goals_home
#         user_prediction_goals_guest = item.prediction_goals_guest
#         user_prediction_match_state = item.prediction_match_state
#         points = 1
#         note = '1.Прогноза за мач: 1 т.'
#         if user_prediction_match_state == match_state:
#             temp_points = 3 * multiplier
#             points += temp_points
#             note = note + f' \n 2.Познат изход от срещата: {temp_points} т.'
#         if user_prediction_goals_home == match_goals_home and user_prediction_goals_guest == match_goals_guest:
#             temp_points = 5 * multiplier
#             points += temp_points
#             note = note + f' \n 3.Познат точен резултат: {temp_points} т.'
#         item.points_gained = points
#         item.prediction_note = note
#         item.save()
#     # calculate ranklist
#     UserScore.objects.all().delete()
#     all_predictions = UserPredictions.objects.all()
#     ranklist = {item.user_id: 0 for item in all_predictions}
#     for item in all_predictions:
#         key = item.user_id
#         points = ranklist[key]
#         points += item.points_gained
#         ranklist[key] = points
#     for item in ranklist:
#         p = UserScore(user_id=item, points=ranklist[item])
#         p.save()


# post_save.connect(score_calculator, sender=Matches)
