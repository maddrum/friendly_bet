from django.db import models
from django.contrib.auth import get_user_model
import datetime


class TotalStats(models.Model):
    users = get_user_model()
    total_predictions = models.IntegerField()
    total_points_gained = models.IntegerField()
    total_match_states_guessed = models.IntegerField()
    total_match_results_guessed = models.IntegerField()
    created_date = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return str(self.created_date)


class UserGuessesNumber(models.Model):
    users = get_user_model()
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    guessed_matches = models.IntegerField()
    guessed_results = models.IntegerField()

    def __str__(self):
        return str(self.user)
