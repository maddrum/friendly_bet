from django.db import models
from events import settings as event_settings


class Event(models.Model):
    event_name = models.CharField(max_length=200)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_name


class EventGroups(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_group')
    event_group = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.group}'


class EventPhases(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_phases')
    phase = models.CharField(max_length=20, choices=event_settings.PHASE_SELECTOR)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)


class EventMatchStates(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_match_states')
    match_state = models.CharField(max_length=20, choices=event_settings.MATCH_STATES)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.match_state}'


class Teams(models.Model):
    group = models.ForeignKey(EventGroups, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100, blank=False, unique=True)
    short_name = models.CharField(max_length=2)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
