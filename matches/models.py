from django.db import models

from events.models import Event, EventPhases, EventGroups, EventMatchStates, Teams


class Matches(models.Model):
    home = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='country_home')
    guest = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='country_guest')
    phase = models.ForeignKey(EventPhases, on_delete=models.PROTECT, related_name='match_phase')
    match_number = models.IntegerField()
    match_start_time = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return_str = f'мач {self.match_number} | {self.home.name} - {self.guest.name} @ {self.match_start_time}'
        return return_str

    class Meta:
        unique_together = ('home', 'guest', 'phase',)
        ordering = ['match_number', ]


class MatchResult(models.Model):
    # !NB has post save signal - signals.py

    match = models.OneToOneField(Matches, on_delete=models.CASCADE, related_name='match_result')
    match_state = models.ForeignKey(EventMatchStates, on_delete=models.PROTECT)
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
