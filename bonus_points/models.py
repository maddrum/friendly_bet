from django.db import models
from django.contrib.auth import get_user_model
import datetime


# Create your models here.
class BonusDescription(models.Model):
    # each bonus must have only one correct answer.
    input_choices = [('text', 'text'), ('number', 'number'), ('all-countries', 'all-countries'),
                     ('choices', 'choices')]
    bonus_name = models.CharField(max_length=200)
    active_until = models.DateTimeField()
    correct_answer = models.CharField(max_length=500, null=True, blank=True)
    points = models.IntegerField()
    participate_link = models.BooleanField(default=False)
    # all users automatically apply for bonuses with participate_link = False.
    bonus_active = models.BooleanField(default=False)
    # only active bonuses will be shown not active bonuses are just a drafts
    input_filed = models.CharField(max_length=20, default='text', choices=input_choices)
    archived = models.BooleanField(default=False)
    available_choices = models.CharField(max_length=600, default='No')

    # for bonuses which have selector field. This field contains comma separated options
    # only taken when 'choices' is selected for input_field

    def __str__(self):
        return str(self.bonus_name) + ' [' + str(self.points) + ' точки]'


class BonusUserPrediction(models.Model):
    # users store their bonus score answers
    user_model = get_user_model()
    user_bonus_name = models.ForeignKey(BonusDescription, on_delete=models.CASCADE, related_name='user_bonus_name')
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, related_name='bonus_user')
    user_prediction = models.CharField(max_length=500)
    points_gained = models.IntegerField(default=0)
    summary_text = models.CharField(max_length=500)
    user_participate = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return str(self.user) + ' ' + str(self.user_bonus_name)


class BonusUserAutoPoints(models.Model):
    # stores points for user points with no participate link
    user_model = get_user_model()
    auto_user_bonus_name = models.ForeignKey(BonusDescription, on_delete=models.CASCADE,
                                             related_name='auto_user_bonus_name')
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, related_name='auto_bonus_user')
    points_gained = models.IntegerField(default=0)
    summary_text = models.CharField(max_length=500)

    def __str__(self):
        return str(self.user) + ' ' + str(self.auto_user_bonus_name)


class UserBonusSummary(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, related_name="user_bonus")
    total_bonus_points = models.IntegerField()
    total_summary = models.TextField()

    def __str__(self):
        return str(self.user) + ":" + str(self.total_bonus_points)
