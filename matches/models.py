from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils import timezone
from django.urls import reverse_lazy
import datetime


class Countries(models.Model):
    group_names = [('Група ' + chr(item), 'Група ' + chr(item)) for item in range(65, 73)]

    name = models.CharField(max_length=100, blank=False, unique=True)
    group = models.CharField(choices=group_names, max_length=10)
    iso_code = models.CharField(max_length=2)

    def __str__(self):
        return self.name


class Matches(models.Model):
    phase_selector = [('group_phase', 'Групова фаза'), ('eighth-finals', 'Осминафинали'),
                      ('quarterfinals', 'Четвъртфинал'), ('semifinals', 'Полуфинал'), ('little_final', 'Малък финал'),
                      ('final', 'Финал')]
    match_states = [('home', 'Победа домакин'), ('guest', 'Победа гост'),
                    ('penalties_home', 'Победа за домакин след дузпи'),
                    ('penalties_guest', 'Победа за гост след дузпи')]

    country_home = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='country_home')
    country_guest = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='country_guest')
    match_number = models.IntegerField(blank=False, null=False)
    match_date = models.DateField()
    match_start_time = models.TimeField()
    match_start_time_utc = models.DateTimeField(default=timezone.now)
    score_home = models.IntegerField(default=0)
    score_guest = models.IntegerField(default=0)
    score_after_penalties_home = models.IntegerField(default=0)
    score_after_penalties_guest = models.IntegerField(default=0)
    match_state = models.CharField(max_length=20, blank=True, choices=match_states)
    penalties = models.BooleanField(default=False)
    phase = models.CharField(max_length=20, choices=phase_selector)
    match_is_over = models.BooleanField(default=False)

    def __str__(self):
        return_str = 'мач ' + str(self.match_number) + ' | ' + str(self.country_home) + ' - ' + str(self.country_guest)
        return return_str

    class Meta:
        unique_together = ('country_home', 'country_guest', 'phase',)


class UserPredictions(models.Model):
    user = get_user_model()
    match_states = Matches().match_states
    user_id = models.ForeignKey(user, on_delete=models.CASCADE, related_name='user')
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='user_predictions')
    prediction_match_state = models.CharField(max_length=20, choices=match_states)
    prediction_goals_home = models.IntegerField(default=0, null=True)
    prediction_goals_guest = models.IntegerField(default=0, null=True)
    gave_prediction = models.BooleanField(default=False)
    prediction_note = models.TextField(default='Дал си прогноза за мача: 1 т.')
    points_gained = models.IntegerField(default=0, null=False)
    # creation and last_edit times. Equal if no edit has been made
    creation_time = models.DateTimeField(default=datetime.datetime.utcnow)
    last_edit = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return str(self.user_id) + " " + str(self.match)

    def get_absolute_url(self):
        return reverse_lazy('accounts:profile')


class UserScore(models.Model):
    user = get_user_model()
    user_id = models.ForeignKey(user, on_delete=models.CASCADE, related_name='user_points')
    points = models.IntegerField(null=True, default=0)
    bonus_points_added = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_id) + ":" + str(self.points)


class EventDates(models.Model):
    event_name = models.CharField(max_length=200)
    event_start_date = models.DateField()
    event_end_date = models.DateField()

    def __str__(self):
        return self.event_name


def score_calculator(sender, instance, created, *args, **kwargs):
    # 1. Calculate points for every user upon saving match result.
    # 2. Calculate ranklist after every match
    # check for match_is_over to be true to continue
    if not instance.match_is_over:
        return
    queryset = UserPredictions.objects.filter(match=instance.id)
    match_goals_home = instance.score_home
    match_goals_guest = instance.score_guest
    match_state = instance.match_state
    # multipliers for quater, semi and finals
    multiplier_definition = {
        'group_phase': 1,
        'eighth-finals': 1,
        'quarterfinals': 2,
        'semifinals': 3,
        'little_final': 3,
        'final': 4,
    }
    multiplier = multiplier_definition[instance.phase]

    for item in queryset:
        user_prediction_goals_home = item.prediction_goals_home
        user_prediction_goals_guest = item.prediction_goals_guest
        user_prediction_match_state = item.prediction_match_state
        points = 1
        note = '1.Прогноза за мач: 1 т.'
        if user_prediction_match_state == match_state:
            temp_points = 3 * multiplier
            points += temp_points
            note = note + f' \n 2.Познат изход от срещата: {temp_points} т.'
        if user_prediction_goals_home == match_goals_home and user_prediction_goals_guest == match_goals_guest:
            temp_points = 5 * multiplier
            points += temp_points
            note = note + f' \n 3.Познат точен резултат: {temp_points} т.'
        item.points_gained = points
        item.prediction_note = note
        item.save()
    # calculate ranklist
    UserScore.objects.all().delete()
    all_predictions = UserPredictions.objects.all()
    ranklist = {item.user_id: 0 for item in all_predictions}
    for item in all_predictions:
        key = item.user_id
        points = ranklist[key]
        points += item.points_gained
        ranklist[key] = points
    for item in ranklist:
        p = UserScore(user_id=item, points=ranklist[item])
        p.save()


post_save.connect(score_calculator, sender=Matches)
