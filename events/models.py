from django.db import models
from events import settings as event_settings
from django.utils.text import slugify
from unidecode import unidecode


class Event(models.Model):
    event_name = models.CharField(max_length=60)
    slug_name = models.SlugField(max_length=180, unique=True, blank=True)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    top_event = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_name

    def slugify_name(self):
        unidecode_name = unidecode(self.event_name)
        self.slug_name = slugify(unidecode_name)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slugify_name()
        return super().save(*args, **kwargs)

    def update_slug(self):
        self.slugify_name()
        self.save()


class EventGroups(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_group')
    event_group = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.event_group}'

    class Meta:
        unique_together = ['event', 'event_group']


class EventPhases(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_phases')
    phase = models.CharField(max_length=20, choices=event_settings.PHASE_SELECTOR)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.get_phase_display()}'

    class Meta:
        unique_together = ['event', 'phase']


class EventMatchStates(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_match_states')
    match_state = models.CharField(max_length=20, choices=event_settings.MATCH_STATES)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.match_state}'

    class Meta:
        unique_together = ['event', 'match_state']


class Teams(models.Model):
    group = models.ForeignKey(EventGroups, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100, blank=False, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.group} -> {self.name}'

    class Meta:
        unique_together = ['group', 'name']
