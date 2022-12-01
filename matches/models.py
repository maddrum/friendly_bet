import datetime

from django.db import models
from django.utils import timezone

from events.models import EventMatchState, EventPhase, Team


class MatchManager(models.Manager):
    def get_matches_for_date(self, date=None, event=None):
        eval_date = timezone.now().date() if date is None else date
        start_time = datetime.datetime.combine(eval_date, datetime.time(0, 0, 1))
        final_time = datetime.datetime.combine(eval_date, datetime.time(23, 59, 59))
        qs = self.get_queryset().filter(match_start_time__gte=start_time, match_start_time__lte=final_time)
        if event is not None:
            qs = qs.filter(phase__event=event)
        return qs


class Match(models.Model):
    home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='country_home')
    guest = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='country_guest')
    phase = models.ForeignKey(EventPhase, on_delete=models.PROTECT, related_name='match_phase')
    match_number = models.IntegerField()
    match_start_time = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    objects = MatchManager()

    def __str__(self):
        return_str = f'мач {self.match_number} | ' \
                     f'{self.home.name} - {self.guest.name} | {self.match_start_time.strftime("%d.%m.%Y - %H:%M")}'
        return return_str

    class Meta:
        unique_together = ('home', 'guest', 'phase',)
        ordering = ['match_start_time']


class MatchResult(models.Model):
    # !NB has post save signal - signals.py

    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='match_result')
    match_state = models.ForeignKey(EventMatchState, on_delete=models.PROTECT)
    score_home = models.IntegerField(default=0)
    score_guest = models.IntegerField(default=0)
    score_after_penalties_home = models.IntegerField(default=0)
    score_after_penalties_guest = models.IntegerField(default=0)
    penalties = models.BooleanField(default=False)
    match_is_over = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.match)
