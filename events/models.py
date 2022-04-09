from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from events import settings as event_settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Event(models.Model):
    event_name = models.CharField(max_length=60)
    slug_name = models.SlugField(max_length=180, unique=True, blank=True)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    top_event = models.BooleanField(default=False)
    event_total_matches = models.IntegerField(default=0)
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


class EventGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_group')
    event_group = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.event_group}'

    class Meta:
        unique_together = ['event', 'event_group']


class EventMatchState(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_match_states')
    match_state = models.CharField(max_length=20, choices=event_settings.MATCH_STATES)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.get_match_state_display()}'

    class Meta:
        unique_together = ['event', 'match_state']


class EventPhase(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_phases')
    phase = models.CharField(max_length=20, choices=event_settings.PHASE_SELECTOR)
    phase_match_states = models.ManyToManyField(EventMatchState)
    multiplier = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.event} -> {self.get_phase_display()}'

    class Meta:
        unique_together = ['event', 'phase']

    def limit_event_phases_choices(self):
        choices = EventMatchState.objects.filter(event=self.event).values_list()
        return choices


class Team(models.Model):
    group = models.ForeignKey(EventGroup, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100, blank=False, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.group} -> {self.name}'

    class Meta:
        unique_together = ['group', 'name']
        ordering = ('-group__event_group', 'name')


class PhaseBetPoint(models.Model):
    phase = models.OneToOneField(EventPhase, on_delete=models.CASCADE, related_name='bet_points')
    points_state = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text='Defines how much points will be TAKEN from the user on FAILED bet on match state.',
    )
    return_points_state = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5000)],
        help_text='Defines how much points will be GIVEN to the user on SUCCESS bet on match state.',
    )
    points_result = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text='Defines how much points will be TAKEN from the user on FAILED bet on match result.',
    )
    return_points_result = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5000)],
        help_text='Defines how much points will be GIVEN from the user on SUCCESS bet on match result.',
    )

    def __str__(self):
        return f'PhaseBetPoints -> {str(self.phase)}'
