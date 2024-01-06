from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from events.models import Event, EventMatchState
from matches.models import Match


class UserPrediction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="predictions")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="match")
    match_state = models.ForeignKey(EventMatchState, on_delete=models.CASCADE)
    goals_home = models.IntegerField(default=0)
    goals_guest = models.IntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + " " + str(self.match)

    class Meta:
        unique_together = ("user", "match")


class BetAdditionalPoint(models.Model):
    prediction = models.OneToOneField(UserPrediction, on_delete=models.CASCADE, related_name="bet_points")
    apply_match_state = models.BooleanField(default=False)
    apply_result = models.BooleanField(default=False)
    points_match_state_to_take = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Points which will be TAKEN FROM the user if match STATE bet fails.",
    )
    points_result_to_take = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Points which will be TAKEN FROM the user if match RESULT bet fails.",
    )
    points_match_state_to_give = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Points which will be GIVEN TO the user if match STATE bet is successful.",
    )
    points_result_to_give = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Points which will be GIVEN TO the user if match RESULT bet is successful.",
    )
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{str(self.prediction)}"


class PredictionPoint(models.Model):
    prediction = models.OneToOneField(UserPrediction, on_delete=models.CASCADE, related_name="prediction_points")
    points_gained = models.IntegerField(default=0, null=False, help_text="Final sum of total points gained")
    base_points = models.IntegerField(default=0, null=False, help_text="Points from base game only")
    additional_points = models.IntegerField(default=0, null=False, help_text="Points from extra bets only")
    note = models.TextField(default="Дал си прогноза за мача: 1 т.")
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.prediction} -> {self.points_gained}"

    def save(self, *args, **kwargs):
        self.points_gained = self.base_points + self.additional_points
        super().save(*args, **kwargs)


class UserScore(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_points")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_points")
    points = models.IntegerField(null=True, default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.event}: {self.points}"
