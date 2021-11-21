from django.contrib.auth import get_user_model
from django.db import models

from bonus_points.settings import INPUT_CHOICES
from events.models import Event


class BonusDescription(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
    name = models.CharField(max_length=200)
    active_until = models.DateTimeField()
    correct_answer = models.CharField(max_length=500, null=True, blank=True)
    points = models.IntegerField()

    available_choices = models.CharField(max_length=600, blank=True, null=True, help_text='CSV of available choices')
    bonus_input = models.CharField(max_length=20, default='text', choices=INPUT_CHOICES)

    auto_bonus = models.BooleanField(default=False,
                                     help_text='If this is checked, all users will be included to '
                                               'participate in this bonus by default.')
    auto_bonus_calculator_function_name = models.CharField(max_length=100, null=True, blank=True)
    bonus_active = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name) + ' [' + str(self.points) + ' точки]'


class BonusUserPrediction(models.Model):
    # users store their bonus score answers
    bonus = models.ForeignKey(BonusDescription, on_delete=models.CASCADE, related_name='bonus')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='bonus_user')
    user_prediction = models.CharField(max_length=500)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} {self.bonus} -> {self.user_prediction}'


class BonusUserScore(models.Model):
    prediction = models.ForeignKey(BonusUserPrediction, on_delete=models.CASCADE, related_name='prediction')
    points_gained = models.IntegerField(default=0)
    summary_text = models.CharField(max_length=500)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.prediction} - {self.points_gained}'


class AutoBonusUserScore(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='auto_bonus_user')
    bonus = models.ForeignKey(BonusDescription, on_delete=models.CASCADE, related_name='auto_bonus_obj')
    points_gained = models.IntegerField(default=0)
    summary_text = models.CharField(max_length=500)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.points_gained}'


class UserBonusSummary(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user")
    total_bonus_points = models.IntegerField(default=0)
    total_summary = models.TextField(blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_bonus', blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + ":" + str(self.total_bonus_points)
