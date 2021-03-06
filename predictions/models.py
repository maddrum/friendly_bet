from django.contrib.auth import get_user_model
from django.db import models

from events.models import Event, EventMatchStates
from matches.models import Matches


class UserPredictions(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='predictions')
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='match')
    match_state = models.ForeignKey(EventMatchStates, on_delete=models.CASCADE)
    goals_home = models.IntegerField(default=0)
    goals_guest = models.IntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + " " + str(self.match)

    class Meta:
        unique_together = ('user', 'match')


class PredictionPoints(models.Model):
    prediction = models.OneToOneField(UserPredictions, on_delete=models.CASCADE, related_name='prediction_points')
    points_gained = models.IntegerField(default=0, null=False)
    note = models.TextField(default='Дал си прогноза за мача: 1 т.')
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.prediction} -> {self.points_gained}'


class UserScores(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_points')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_points')
    points = models.IntegerField(null=True, default=0)
    bonus_points_added = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} -> {self.event}: {self.points}'
