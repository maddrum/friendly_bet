from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy

from events.models import Event, EventMatchStates
from matches.models import Matches


class UserPredictions(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='predictions')
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='match')
    match_state = models.ForeignKey(EventMatchStates, on_delete=models.CASCADE)
    goals_home = models.IntegerField(default=0)
    goals_guest = models.IntegerField(default=0)
    summary = models.TextField(default='Дал си прогноза за мача: 1 т.')
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_id) + " " + str(self.match)

    def get_absolute_url(self):
        return reverse_lazy('accounts:profile')


class UserMatchPoints(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_match_points')
    match = models.ForeignKey(Matches, on_delete=models.CASCADE)
    points_gained = models.IntegerField(default=0, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)


class UserScores(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_points')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_points')
    points = models.IntegerField(null=True, default=0)
    bonus_points_added = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} -> {self.event}: {self.points}'
